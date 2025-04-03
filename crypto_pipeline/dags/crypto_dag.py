from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, to_date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_csv():
    logger.info("Starting upload_csv")
    client = storage.Client()
    logger.info("Got storage client")
    bucket = client.get_bucket("bitcoin-data-bucket-2025")
    logger.info("Got bucket")
    blob = bucket.blob("raw/btc_1d_data_2018_to_2025.csv")
    logger.info("Created blob")
    blob.upload_from_filename("/Users/neogami/Desktop/Final-Project_DEZ2025/Final-Project_DEZ2025/btc_1d_data_2018_to_2025.csv")
    logger.info("CSV uploaded!")

def transform_data():
    logger.info("Starting transform_data")
    spark = SparkSession.builder \
        .appName("BitcoinTransform") \
        .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.23.2") \
        .getOrCreate()
    logger.info("Spark session created")
    df = spark.read.format("bigquery") \
        .option("table", "final-project-dez2025.crypto_data.raw_prices") \
        .load()
    logger.info("Data loaded from BigQuery")
    df = df.withColumn("date", to_date(col("Open time"), "yyyy-MM-dd"))
    df = df.withColumn("price_range", col("High") - col("Low"))
    yearly_avg = df.groupBy(df.date.substr(1, 4).alias("year")) \
                   .agg(avg("Number of trades").alias("avg_trades"))
    df.select("date", "price_range").write.format("bigquery") \
        .option("table", "final-project-dez2025.crypto_data.daily_range") \
        .option("temporaryGcsBucket", "bitcoin-data-bucket-2025") \
        .mode("overwrite") \
        .save()
    yearly_avg.write.format("bigquery") \
        .option("table", "final-project-dez2025.crypto_data.yearly_trades") \
        .option("temporaryGcsBucket", "bitcoin-data-bucket-2025") \
        .mode("overwrite") \
        .save()
    logger.info("Transformed and saved!")
    spark.stop()

with DAG(
    "crypto_pipeline",
    start_date=datetime(2025, 3, 30),
    schedule_interval=None,
    catchup=False,
) as dag:
    upload_task = PythonOperator(
        task_id="upload_csv",
        python_callable=upload_csv,
    )
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )
    upload_task >> transform_task