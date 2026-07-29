import json
import logging
import os
import uuid
from datetime import UTC, datetime

import pyarrow as pa
from confluent_kafka import Consumer, Producer
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError
from pyiceberg.types import IntegerType, LongType, StringType

TABLE_IDENTIFIER = "my_db.my_table"
TOPIC = os.getenv("KAFKA_TOPIC", "my_topic")
DLQ_TOPIC = os.getenv("KAFKA_DLQ_TOPIC", f"{TOPIC}_dlq")
LOGGER = logging.getLogger(__name__)
EVENT_SCHEMA = pa.schema([
    ("id", pa.int64()),
    ("data", pa.string()),
    ("event_id", pa.string()),
    ("kafka_partition", pa.int32()),
    ("kafka_offset", pa.int64()),
    ("ingested_at", pa.string()),
])
REQUIRED_COLUMNS = {
    "event_id": StringType(),
    "kafka_partition": IntegerType(),
    "kafka_offset": LongType(),
    "ingested_at": StringType(),
}


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
        table = catalog.load_table(TABLE_IDENTIFIER)
    except NoSuchTableError:
        return catalog.create_table(TABLE_IDENTIFIER, schema=EVENT_SCHEMA)

    existing_columns = set(table.schema().column_names)
    missing_columns = REQUIRED_COLUMNS.keys() - existing_columns
    if missing_columns:
        with table.update_schema() as update:
            for column_name in sorted(missing_columns):
                update.add_column(column_name, REQUIRED_COLUMNS[column_name])
    return catalog.load_table(TABLE_IDENTIFIER)


def normalize_message(message) -> dict[str, object]:
    try:
        payload = json.loads(message.value().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("message value must be UTF-8 JSON") from error

    if not isinstance(payload, dict):
        raise ValueError("event must be a JSON object")
    if type(payload.get("id")) is not int or payload["id"] <= 0:
        raise ValueError("event.id must be a positive integer")
    if not isinstance(payload.get("data"), str) or not payload["data"].strip():
        raise ValueError("event.data must be a non-empty string")

    event_id = payload.get("event_id")
    if event_id is not None and not isinstance(event_id, str):
        raise ValueError("event.event_id must be a string when provided")
    message_identity = f"{message.topic()}:{message.partition()}:{message.offset()}"
    event_id = event_id or str(uuid.uuid5(uuid.NAMESPACE_URL, message_identity))
    return {
        "id": payload["id"],
        "data": payload["data"].strip(),
        "event_id": event_id,
        "kafka_partition": message.partition(),
        "kafka_offset": message.offset(),
        "ingested_at": datetime.now(UTC).isoformat(),
    }


def send_to_dlq(producer: Producer, message, error: Exception) -> None:
    producer.produce(
        DLQ_TOPIC,
        json.dumps(
            {
                "error": str(error),
                "topic": message.topic(),
                "partition": message.partition(),
                "offset": message.offset(),
                "value": message.value().decode("utf-8", errors="replace"),
            }
        ).encode("utf-8"),
    )
    producer.poll(0)


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
    dlq_producer = Producer({"bootstrap.servers": "kafka:29092"})
    consumer.subscribe([TOPIC])

    batch = []
    try:
        for _ in range(max_messages):
            message = consumer.poll(poll_timeout)
            if message is None:
                break
            if message.error():
                raise RuntimeError(f"Kafka error: {message.error()}")
            try:
                batch.append(normalize_message(message))
            except ValueError as error:
                send_to_dlq(dlq_producer, message, error)
                LOGGER.warning("invalid_event_sent_to_dlq", extra={"offset": message.offset()})

        pending_dlq_messages = dlq_producer.flush(10)
        if pending_dlq_messages:
            raise RuntimeError(f"Timed out delivering {pending_dlq_messages} DLQ message(s)")

        if batch:
            table.append(pa.Table.from_pylist(batch, schema=EVENT_SCHEMA))
        consumer.commit(asynchronous=False)
        LOGGER.info("kafka_batch_committed", extra={"records_written": len(batch)})
        return len(batch)
    finally:
        consumer.close()


if __name__ == "__main__":
    run_sync()
