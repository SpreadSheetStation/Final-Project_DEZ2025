FROM apache/airflow:2.9.0-python3.11
USER root

RUN apt-get update && apt-get install -y curl procps && apt-get clean

RUN mkdir -p /usr/lib/jvm/ && \
    curl -L -o /tmp/openjdk.tar.gz https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz && \
    tar xzf /tmp/openjdk.tar.gz -C /usr/lib/jvm/ && \
    rm /tmp/openjdk.tar.gz
ENV JAVA_HOME=/usr/lib/jvm/jdk-11.0.2
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow

RUN pip install --no-cache-dir \
    kagglehub[pandas-datasets] google-cloud-storage google-cloud-bigquery \
    pyspark==3.5.1 pandas python-dotenv psycopg2-binary

RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts
ENV PATH=$PATH:/home/airflow/google-cloud-sdk/bin

RUN mkdir -p /home/airflow/spark-jars
RUN curl -L -o /home/airflow/spark-jars/spark-bigquery-with-dependencies_2.12-0.27.0.jar \
    https://repo1.maven.org/maven2/com/google/cloud/spark/spark-bigquery-with-dependencies_2.12/0.27.0/spark-bigquery-with-dependencies_2.12-0.27.0.jar && \
    curl -L -o /home/airflow/spark-jars/gcs-connector-hadoop3-2.2.22-shaded.jar \
    https://repo1.maven.org/maven2/com/google/cloud/bigdataoss/gcs-connector/hadoop3-2.2.22/gcs-connector-hadoop3-2.2.22-shaded.jar && \
    curl -L -o /home/airflow/spark-jars/guava-31.0.1-jre.jar \
    https://repo1.maven.org/maven2/com/google/guava/guava/31.0.1-jre/guava-31.0.1-jre.jar && \
    curl -L -o /home/airflow/spark-jars/google-api-client-1.35.2.jar \
    https://repo1.maven.org/maven2/com/google/api-client/google-api-client/1.35.2/google-api-client-1.35.2.jar

ENV AIRFLOW_HOME=/opt/airflow

COPY crypto_pipeline/dags/ /opt/airflow/dags/

ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/final-project-creds.json