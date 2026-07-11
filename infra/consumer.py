import json
import pyarrow as pa
from confluent_kafka import Consumer, KafkaError
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType

catalog = load_catalog(
    "default",
    **{"type": "sql", "uri": "sqlite:///iceberg_catalog.db", "warehouse": "./warehouse"}
)

try:
    table = catalog.load_table("my_db.my_table")
except Exception:
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=IntegerType(), required=True),
        NestedField(field_id=2, name="data", field_type=StringType(), required=False),
    )
    table = catalog.create_table("my_db.my_table", schema=schema)

consumer = Consumer({
    'bootstrap.servers': '127.0.0.1:9092',
    'group.id': 'my-python-consumer',
    'auto.offset.reset': 'earliest',
})
consumer.subscribe(['my_topic'])

arrow_schema = pa.schema([('id', pa.int32()), ('data', pa.string())])

print("Consumer запущен и ждет сообщения...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Ошибка Kafka: {msg.error()}")
            continue
            
        data = json.loads(msg.value().decode('utf-8'))
        arrow_table = pa.Table.from_pylist([data], schema=arrow_schema)
        table.append(arrow_table)
        print(f"Успешно записано: {data}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()