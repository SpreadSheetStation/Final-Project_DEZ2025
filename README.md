# Final-Project_DEZ2025
Hello there! Welcome to my Final Project for the Data Engineering Zoomcamp 2025!

## Bitcoin Trading Patterns Pipeline
This project delivers a fully automated, Dockerized data pipeline to analyze Bitcoin trading patterns from 2018 to 2025. It pulls daily candlestick data from Kaggle’s “Bitcoin Historical Datasets 2018-2024” (sourced via Binance API), processes it with PySpark, and stores it in Google BigQuery for trading insights. Built with modern tools like Terraform, Airflow, and Docker, it’s portable, scalable, and ready for visualization in Looker Studio.

### Project Overview
- **Goal**: Help investors understand Bitcoin price volatility and trading activity with metrics like average price, price range, and VWAP.
- **Data**: Daily candlesticks (2018-2025) from Kaggle, updated daily via Binance API.
- **Workflow**: Extract (Kaggle API), Load (GCS/BigQuery), Transform (PySpark) — an **ELT** pipeline orchestrated by Airflow.

### Tech Stack
- **Python**: Core language for scripting and DAG logic.
- **Apache Airflow**: Orchestrates the daily pipeline (pull, load, transform).
- **Docker**: Containers for Airflow, PySpark, and Postgres—ensures portability and consistency.
- **PostgreSQL**: Airflow’s metadata database (replaced SQLite for reliability).
- **Terraform**: Provisions Google Cloud infrastructure (GCS bucket, BigQuery dataset).
- **Google Cloud Platform (GCP)**:
  - **Google Cloud Storage (GCS)**: Stores raw CSV data (`gs://bitcoin-data-bucket-2025/raw/`).
  - **Google BigQuery**: Data warehouse for raw (`raw_prices`) and transformed (`daily_range`) tables.
- **PySpark**: Batch processes data into trading metrics.
- **Kaggle API**: Pulls the latest dataset (`btc_1d_data_2018_to_2025.csv`) via `kagglehub`.
- **Looker Studio**: Planned dashboard for visualizing price trends and volatility (in progress).

### Pipeline Steps (ELT)
1. **Extract**: 
   - **Tool**: Kaggle API (`kagglehub`).
   - **Action**: Pulls `btc_1d_data_2018_to_2025.csv` daily from Kaggle.
   - **Output**: Raw CSV uploaded to GCS (`gs://bitcoin-data-bucket-2025/raw/`).
2. **Load**: 
   - **Tool**: Google Cloud Storage → BigQuery.
   - **Action**: Loads raw CSV into BigQuery `raw_prices` table (schema autodetected, `WRITE_TRUNCATE`).
   - **Output**: `final-project-dez2025.crypto_data.raw_prices`.
3. **Transform**: 
   - **Tool**: PySpark.
   - **Action**: Computes metrics (`avg_price`, `price_range`, `price_range_pct`, `vwap`) from `raw_prices`, saves to `daily_range`.
   - **Output**: `final-project-dez2025.crypto_data.daily_range`.

*Why ELT?* Data is loaded raw into BigQuery first (Load), then transformed with PySpark (Transform)—leveraging BigQuery’s storage and Spark’s processing power.

### Setup Instructions
#### Prerequisites
- Docker & Docker Compose
- Git
- Google Cloud credentials (`final-project-creds.json`)

#### Run It
1. **Clone the Repo**:
   ```bash
   git clone <your-repo-url>
   cd Final-Project_DEZ2025

2. **Start Docker**:
    ```bash
    docker-compose up -d --build

- Builds bitcoin-pipeline-airflow:latest.
- Starts Postgres, Airflow webserver, scheduler, and initializes the DB.

3. **Access Airflow UI**:
- URL: http://localhost:8080
- Login: admin / admin

4. **Trigger Pipeline**:
    ```bash
    docker exec <scheduler_container_id> airflow dags trigger crypto_pipeline

- Find <scheduler_container_id> with docker ps (e.g. final-project_dez2025-airflow-scheduler-1).

5. **Monitor**:
- UI: Watch crypto_pipeline run (pull_kaggle_data → load_to_bigquery → transform_data).
- Logs: docker logs <scheduler_container_id>.

## Infrastructure
**Terraform**:
    ```bash
    cd terraform
    terraform init
    terraform apply

Creates bitcoin-data-bucket-2025 (GCS) and final-project-dez2025.crypto_data (BigQuery).

## Outputs
GCS: gs://bitcoin-data-bucket-2025/raw/btc_1d_data_2018_to_2025.csv (daily updated).

BigQuery:
- raw_prices: Raw candlesticks (~2,648+ rows, growing daily).
- daily_range: Transformed metrics (date, avg_price, price_range, price_range_pct, vwap).

