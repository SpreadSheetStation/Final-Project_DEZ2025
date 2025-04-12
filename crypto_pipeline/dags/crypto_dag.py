from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import logging
import kagglehub
import pandas as pd
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pull_kaggle_data():
    """Pulls daily Bitcoin data from Kaggle and uploads to GCS."""
    logger.info("Starting pull_kaggle_data")
    df = kagglehub.load_dataset(
        kagglehub.KaggleDatasetAdapter.PANDAS,
        "novandraanugrah/bitcoin-historical-datasets-2018-2024",
        "btc_1d_data_2018_to_2025.csv"
    )
    local_file = "/tmp/btc_1d_data_2018_to_2025.csv"
    df.to_csv(local_file, index=False)
    logger.info(f"Dataset pulled and saved to {local_file}")
    client = storage.Client()
    bucket = client.get_bucket("bitcoin-data-bucket-2025")
    blob = bucket.blob("raw/btc_1d_data_2018_to_2025.csv")
    blob.upload_from_filename(local_file)
    logger.info("Uploaded to GCS!")
    os.remove(local_file)

def load_to_bigquery():
    """Loads CSV from GCS to BigQuery raw_prices table with daily partitioning."""
    logger.info("Starting load_to_bigquery")
    client = bigquery.Client()
    table_id = "final-project-dez2025.crypto_data.raw_prices"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="Open time"  # Partition by daily timestamp
        )
    )
    uri = "gs://bitcoin-data-bucket-2025/raw/btc_1d_data_2018_to_2025.csv"
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    logger.info("CSV loaded to BigQuery as raw_prices with daily partitioning")

def transform_data():
    """Transforms raw_prices to daily_range with PySpark and daily partitioning."""
    logger.info("Starting transform_data")
    spark = SparkSession.builder \
        .appName("BitcoinTransform") \
        .config("spark.jars", "/home/airflow/spark-jars/spark-bigquery-with-dependencies_2.12-0.27.0.jar,/home/airflow/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar,/home/airflow/spark-jars/guava-31.0.1-jre.jar,/home/airflow/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.driver.extraClassPath", "/home/airflow/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar:/home/airflow/spark-jars/guava-31.0.1-jre.jar:/home/airflow/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.executor.extraClassPath", "/home/airflow/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar:/home/airflow/spark-jars/guava-31.0.1-jre.jar:/home/airflow/spark-jars/google-api-client-1.35.2.jar") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.pyspark.python", "python3") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/airflow/final-project-creds.json") \
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
        df = df.withColumn("avg_price", (col("Open") + col("Close")) / 2)
        df = df.withColumn("price_range", col("High") - col("Low"))
        df = df.withColumn("price_range_pct", (col("High") - col("Low")) / col("Low") * 100)
        df = df.withColumn("vwap", (col("Open") + col("High") + col("Low") + col("Close")) / 4)
        df.select("Open time", "avg_price", "price_range", "price_range_pct", "vwap") \
            .withColumnRenamed("Open time", "date") \
            .write.format("bigquery") \
            .option("table", "final-project-dez2025.crypto_data.daily_range") \
            .option("temporaryGcsBucket", "bitcoin-data-bucket-2025") \
            .option("partitionField", "date") \
            .option("partitionType", "DAY") \
            .mode("overwrite") \
            .save()
        logger.info("Transformed and saved daily_range with daily partitioning")
    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
        raise
    spark.stop()

with DAG(
    "crypto_pipeline",
    start_date=datetime(2025, 3, 30),
    schedule_interval="@daily",
    catchup=False,
    description="Pipeline to pull Bitcoin daily candlesticks from Kaggle, load to BigQuery, and transform with PySpark",
) as dag:
    pull_task = PythonOperator(
        task_id="pull_kaggle_data",
        python_callable=pull_kaggle_data,
    )
    load_bq_task = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_to_bigquery,
    )
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )
    pull_task >> load_bq_task >> transform_task