"""Compatibility entry point for running the Kafka-to-Iceberg batch consumer."""

from kafka_to_iceberg_run import run_sync


if __name__ == "__main__":
    run_sync()
