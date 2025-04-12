# Bitcoin Trading Data Pipeline ( Final-Project_DEZ2025 ) 
Hello there! Welcome to my Final Project for the Data Engineering Zoomcamp 2025!

## Table of Contents
- [Project Introduction](#project-introduction)
- [Problem Description](#problem-description)
- [Tech Stack](#tech-stack)


### Project Introduction
This project delivers a fully automated, Dockerized data pipeline to analyze Bitcoin trading data from 2018 to present (updated daily as of April 2025).
Built with modern tools like Terraform, Airflow, and Docker, it’s portable, scalable, and ready for actionable trading metrics from daily candlesticks for Long-term Investing, Trading and Backtesting of Bitcoin.

### Project Overview
- **Goal**: Help investors understand Bitcoin price volatility and trading activity with metrics like average price, price range, and VWAP.
- **Data**: Daily candlesticks (2018-2025) from Kaggle, updated daily via Binance API.
- **Workflow**: Extract (Kaggle API), Load (GCS/BigQuery), Transform (PySpark) — an **ELT** pipeline orchestrated by Airflow.

### Problem description
As a trader with 6+ years experience, I know it can be very confusing to have too much indicators drawn on a single trading chart. Over the years I experienced the concept of "less is more" on my trading charts to be real. Visual over-lays on candle stick charts can be nice, but can also be very overwhelming, leading to analysis-paralysis for a lot of traders/investors. 

Also not all Data is always clearly shown on charts and it still requires precision to hover your mouse cursor over certain spots you want to see some actual metric-numbers about.

To have all this data neatly organised and presented with a Dashboard gives an advantage by keeping a clear overview when making trade decisions or while backtesting Trades on Bitcoin; without the chance over overwhelming a trader with TOO MANY stacked indicators on a single trading chart.

The majority of traders lose money (which is a commonly known fact). Besides a well developed strategy & mindset, the winning edge isn't found in having extra indicators stacked, but in proper and clear organisation of data, which will lead to a better comprehension of the price action. On chart indicators are often used in a visual relative way and— with X&Y-axis stretched/compressed to personal preferences —it can often be very misleading what a "big" or "small" candlestick or volume bar is. Actual data and numbers are for advanced traders who prefer to dive deeper. This is what this data pipeline is providing to traders who use the 1Day Timeframe (which is an important time frame for swing traders) to trade/invest in Bitcoin and backtest their Bitcoin trades/investments.

### (ELT) Pipeline Steps explained
1. **Extract**: 
It pulls the Raw Data (OHLCV market data with trade execution metrics) of the Bitcoin Daily Candle Timeframe from Kaggle’s [“Bitcoin Historical Datasets 2018-2025”](https://www.kaggle.com/datasets/novandraanugrah/bitcoin-historical-datasets-2018-2024?select=btc_1d_data_2018_to_2025.csv), 
   - **Tool**: Kaggle API (`kagglehub`).
   - **Action**: Pulls `btc_1d_data_2018_to_2025.csv` daily from Kaggle.
   - **Output**: Raw CSV uploaded to GCS (`gs://bitcoin-data-bucket-2025/raw/`).
2. **Load**: 
The Raw Data which has landed in a Google Cloud Storage bucket will then be loaded into BigQuery (Data Warehouse).
   - **Tool**: Google Cloud Storage → BigQuery.
   - **Action**: Loads raw CSV into BigQuery `raw_prices` table (schema autodetected, `WRITE_TRUNCATE`).
   - **Output**: `final-project-dez2025.crypto_data.raw_prices`.
3. **Transform**: 
The Raw Data is then transformed with PySpark to Enhanced Data (Trading Metrics), and stored in Google BigQuery for trading insights.
   - **Tool**: PySpark.
   - **Action**: Computes metrics (`avg_price`, `price_range`, `price_range_pct`, `vwap`) from `raw_prices`, saves to `daily_range`.
   - **Output**: `final-project-dez2025.crypto_data.daily_range`.

*Why ELT?* Data is loaded raw into BigQuery first (Load), then transformed with PySpark (Transform)—leveraging BigQuery’s storage and Spark’s processing power.




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

### Setup Instructions
#### Prerequisites
- Docker & Docker Compose
- Git
- Google Cloud credentials (`final-project-creds.json`) — Ensure it has GCS and BigQuery permissions.

#### Run It
1. **Clone the Repo**:
   ```bash
   git clone <your-repo-url>
   cd Final-Project_DEZ2025```

2. **Start Docker**:
    ```bash
    docker-compose up -d --build```

- Builds bitcoin-pipeline-airflow:latest.
- Starts Postgres, Airflow webserver, scheduler, and initializes the DB.

3. **Access Airflow UI**:
- URL: http://localhost:8080
- Login: admin / admin

4. **Trigger Pipeline**:
    ```bash
    docker exec <scheduler_container_id> airflow dags trigger crypto_pipeline```

- Find <scheduler_container_id> with docker ps (e.g. final-project_dez2025-airflow-scheduler-1).

5. **Monitor**:
- UI: Watch crypto_pipeline run (pull_kaggle_data → load_to_bigquery → transform_data).
- Logs: docker logs <scheduler_container_id>.


### Infrastructure
1. Terraform Setup
   ```bash
   cd terraform
   terraform init
   terraform apply

- Creates bitcoin-data-bucket-2025 (GCS) and final-project-dez2025.crypto_data (BigQuery).

## Outputs
Terraform-managed infrastructure

GCS: gs://bitcoin-data-bucket-2025/raw/btc_1d_data_2018_to_2025.csv (daily updated).

BigQuery:
- raw_prices: Raw OHLCV market data with trade execution metrics (~2,648+ rows, growing daily).
- daily_range: Transformed metrics (date, avg_price, price_range, price_range_pct, vwap).

