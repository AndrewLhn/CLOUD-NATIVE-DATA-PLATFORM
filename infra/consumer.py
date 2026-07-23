"""Run the same consumer locally, with Docker services exposed on localhost."""

import os

os.environ.setdefault(
    "ICEBERG_CATALOG_URI",
    "postgresql+psycopg2://airflow:airflow@127.0.0.1:5432/iceberg_metadata",
)
os.environ.setdefault("ICEBERG_WAREHOUSE", "s3://warehouse/")
os.environ.setdefault("MINIO_ENDPOINT", "http://127.0.0.1:9000")
os.environ.setdefault("MINIO_ROOT_USER", "minioadmin")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "minioadmin")

from dags.kafka_to_iceberg_run import run_sync  # noqa: E402

if __name__ == "__main__":
    run_sync()
