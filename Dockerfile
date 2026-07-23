FROM apache/airflow:2.10.0

USER airflow

# Keep Iceberg dependencies separate from Airflow's own Python environment.
RUN python -m venv /home/airflow/iceberg_env && \
    /home/airflow/iceberg_env/bin/pip install --no-cache-dir \
      confluent-kafka==2.4.0 \
      pyarrow==14.0.1 \
      "pyiceberg[sql-postgres,pyarrow]==0.6.0" \
      psycopg2-binary==2.9.9
