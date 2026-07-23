import json
import os

import pyarrow as pa
from confluent_kafka import Consumer
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError

TABLE_IDENTIFIER = "my_db.my_table"
EVENT_SCHEMA = pa.schema([
    ("id", pa.int64()),
    ("data", pa.string()),
])


def get_catalog():
    return load_catalog(
        "default",
        **{
            "type": "sql",
            "uri": os.environ["ICEBERG_CATALOG_URI"],
            "warehouse": os.environ["ICEBERG_WAREHOUSE"],
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
            "s3.endpoint": os.environ["MINIO_ENDPOINT"],
            "s3.access-key-id": os.environ["MINIO_ROOT_USER"],
            "s3.secret-access-key": os.environ["MINIO_ROOT_PASSWORD"],
            "s3.region": "us-east-1",
            "s3.path-style-access": "true",
        },
    )


def get_table(catalog):
    if not catalog.namespace_exists("my_db"):
        catalog.create_namespace("my_db")

    try:
        return catalog.load_table(TABLE_IDENTIFIER)
    except NoSuchTableError:
        return catalog.create_table(TABLE_IDENTIFIER, schema=EVENT_SCHEMA)


def run_sync(max_messages: int = 100, poll_timeout: float = 1.0) -> int:
    catalog = get_catalog()
    table = get_table(catalog)
    consumer = Consumer(
        {
            "bootstrap.servers": "kafka:29092",
            "group.id": "airflow-iceberg-consumer",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe(["my_topic"])

    batch = []
    try:
        for _ in range(max_messages):
            message = consumer.poll(poll_timeout)
            if message is None:
                break
            if message.error():
                raise RuntimeError(f"Kafka error: {message.error()}")
            batch.append(json.loads(message.value().decode("utf-8")))

        if not batch:
            print("No new Kafka messages.")
            return 0

        table.append(pa.Table.from_pylist(batch, schema=EVENT_SCHEMA))
        consumer.commit(asynchronous=False)
        print(f"Written {len(batch)} message(s) to {TABLE_IDENTIFIER}.")
        return len(batch)
    finally:
        consumer.close()


if __name__ == "__main__":
    run_sync()
