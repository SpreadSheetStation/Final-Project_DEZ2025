from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, to_date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_csv():
    """Uploads local Bitcoin CSV to GCS."""
    logger.info("Starting upload_csv")
    client = storage.Client()
    logger.info("Got storage client")
    bucket = client.get_bucket("bitcoin-data-bucket-2025")
    logger.info("Got bucket")
    blob = bucket.blob("raw/btc_1d_data_2018_to_2025.csv")
    logger.info("Created blob")
    blob.upload_from_filename("/workspaces/Final-Project_DEZ2025/btc_1d_data_2018_to_2025.csv")
    logger.info("CSV uploaded!")

def load_to_bigquery():
    """Loads CSV from GCS to BigQuery raw_prices table."""
    logger.info("Starting load_to_bigquery")
    client = bigquery.Client()
    table_id = "final-project-dez2025.crypto_data.raw_prices"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",  # Overwrites table each run
    )
    uri = "gs://bitcoin-data-bucket-2025/raw/btc_1d_data_2018_to_2025.csv"
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    logger.info("CSV loaded to BigQuery as raw_prices")

def transform_data():
    """Transforms raw_prices to daily_range with avg_price, price_range, price_range_pct, and vwap using Spark."""
    logger.info("Starting transform_data")
    spark = SparkSession.builder \
        .appName("BitcoinTransform") \
        .config("spark.jars", "/home/codespace/spark-jars/spark-bigquery-with-dependencies_2.12-0.27.0.jar,/home/codespace/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar,/home/codespace/spark-jars/guava-31.0.1-jre.jar,/home/codespace/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.driver.extraClassPath", "/home/codespace/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar:/home/codespace/spark-jars/guava-31.0.1-jre.jar:/home/codespace/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.executor.extraClassPath", "/home/codespace/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar:/home/codespace/spark-jars/guava-31.0.1-jre.jar:/home/codespace/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.pyspark.python", "python3") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/workspaces/Final-Project_DEZ2025/terraform/final-project-creds.json") \
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
        .getOrCreate()
    logger.info("Spark session created")

    df = spark.read.format("bigquery") \
        .option("table", "final-project-dez2025.crypto_data.raw_prices") \
        .load()
    logger.info("Data loaded from BigQuery")
    logger.info(f"Columns in raw_prices: {df.columns}")

    try:
        # Transformations
        df = df.withColumn("avg_price", (col("Open") + col("Close")) / 2)
        df = df.withColumn("price_range", col("High") - col("Low"))
        df = df.withColumn("price_range_pct", (col("High") - col("Low")) / col("Low") * 100)
        df = df.withColumn("vwap", (col("Open") + col("High") + col("Low") + col("Close")) / 4)
        df.select("Open time", "avg_price", "price_range", "price_range_pct", "vwap") \
            .withColumnRenamed("Open time", "date") \
            .write.format("bigquery") \
            .option("table", "final-project-dez2025.crypto_data.daily_range") \
            .option("temporaryGcsBucket", "bitcoin-data-bucket-2025") \
            .mode("overwrite") \
            .save()
        logger.info("Transformed and saved daily_range with avg_price, price_range, price_range_pct, and vwap!")
    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
        raise
    spark.stop()

# DAG to process Bitcoin data: upload CSV to GCS, load to BigQuery, transform with Spark
with DAG(
    "crypto_pipeline",
    start_date=datetime(2025, 3, 30),
    schedule_interval="@daily",
    catchup=False,
    description="Pipeline to ingest, load, and transform Bitcoin price data",
) as dag:
    upload_task = PythonOperator(
        task_id="upload_csv",
        python_callable=upload_csv,
    )
    load_bq_task = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_to_bigquery,
    )
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )
    upload_task >> load_bq_task >> transform_task