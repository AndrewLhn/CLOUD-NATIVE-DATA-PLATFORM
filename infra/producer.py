import json
import os
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "my_topic")


def delivery_report(error, message):
    if error is not None:
        raise RuntimeError(f"Kafka delivery failed: {error}")
    print(
        f"Message delivered to {message.topic()} "
        f"[partition={message.partition()}, offset={message.offset()}]"
    )


def main() -> None:
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    data = {
        "id": 1,
        "data": "hello world from python",
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }
    producer.produce(TOPIC, json.dumps(data).encode("utf-8"), on_delivery=delivery_report)

    pending_messages = producer.flush(10)
    if pending_messages:
        raise RuntimeError(f"Timed out delivering {pending_messages} Kafka message(s)")


if __name__ == "__main__":
    main()
