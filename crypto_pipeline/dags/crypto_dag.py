from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from google.cloud import storage
from google.cloud import bigquery
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import logging
import kagglehub
import pandas as pd
import os
import traceback

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
    
    try:
        # Load raw_prices
        df = spark.read.format("bigquery") \
            .option("table", "final-project-dez2025.crypto_data.raw_prices") \
            .load()
        logger.info(f"Columns in raw_prices: {df.columns}")
        
        # Verify column names
        expected_columns = ['Open time', 'Open', 'High', 'Low', 'Close']
        actual_columns = df.columns
        for col_name in expected_columns:
            if col_name not in actual_columns:
                logger.error(f"Column '{col_name}' not found in raw_prices. Available columns: {actual_columns}")
                raise ValueError(f"Column '{col_name}' not found in raw_prices")
        
        # Transformations
        df = df.withColumn("avg_price", (col("Open") + col("Close")) / 2)
        df = df.withColumn("price_range", col("High") - col("Low"))
        df = df.withColumn("price_range_pct", (col("High") - col("Low")) / col("Low") * 100)
        df = df.withColumn("vwap", (col("Open") + col("High") + col("Low") + col("Close")) / 4)
        df = df.withColumn("candle_color", 
                          when(col("Close") > col("Open"), "Green").otherwise("Red"))
        df = df.withColumn("volatility_level",
                          when(col("price_range_pct") < 3, "Low")
                          .when((col("price_range_pct") >= 3) & (col("price_range_pct") < 7), "Medium")
                          .otherwise("High"))
        
        # Select and rename
        df_transformed = df.select(
            col("Open time").cast("TIMESTAMP").alias("date"),
            col("avg_price").cast("DOUBLE"),
            col("price_range").cast("DOUBLE"),
            col("price_range_pct").cast("DOUBLE"),
            col("vwap").cast("DOUBLE"),
            col("candle_color").cast("STRING"),
            col("volatility_level").cast("STRING")
        )
        
        # Define explicit schema
        schema = StructType([
            StructField("date", TimestampType(), False),
            StructField("avg_price", DoubleType(), False),
            StructField("price_range", DoubleType(), False),
            StructField("price_range_pct", DoubleType(), False),
            StructField("vwap", DoubleType(), False),
            StructField("candle_color", StringType(), False),
            StructField("volatility_level", StringType(), False)
        ])
        
        # Apply schema
        df_transformed = spark.createDataFrame(df_transformed.rdd, schema)
        
        # Write to BigQuery (no partitioning/clustering for now)
        df_transformed.write.format("bigquery") \
            .option("table", "final-project-dez2025.crypto_data.daily_range") \
            .option("temporaryGcsBucket", "bitcoin-data-bucket-2025") \
            .option("partitionField", "date") \
            .option("partitionType", "DAY") \
            .mode("overwrite") \
            .save()
        logger.info("Transformed and saved daily_range!")
    except Exception as e:
        logger.error(f"Transform failed with error: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise
    
    finally:
        spark.stop()

def partition_cluster_data():
    """Creates a partitioned and clustered daily_range_partitioned table in BigQuery."""
    logger.info("Starting partition_cluster_data")
    client = bigquery.Client()
    try:
        # SQL to create partitioned/clustered table
        query = """
        CREATE OR REPLACE TABLE `final-project-dez2025.crypto_data.daily_range_partitioned`
        PARTITION BY DATE(date)
        CLUSTER BY volatility_level
        AS
        SELECT * 
        FROM `final-project-dez2025.crypto_data.daily_range`
        """
        query_job = client.query(query)
        query_job.result()  # Wait for completion
        logger.info("Created daily_range_partitioned with date partitioning and volatility_level clustering")
    except Exception as e:
        logger.error(f"Partitioning/clustering failed with error: {str(e)}")
        raise

with DAG(
    "crypto_pipeline",
    start_date=datetime(2025, 3, 30),
    schedule_interval="@daily",
    catchup=False,
    description="Pipeline to pull Bitcoin daily candlesticks from Kaggle, load to BigQuery, transform with PySpark, and partition/cluster with BigQuery",
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
    partition_cluster_task = PythonOperator(
        task_id="partition_cluster_data",
        python_callable=partition_cluster_data,
    )
    pull_task >> load_bq_task >> transform_task >> partition_cluster_task