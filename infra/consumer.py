import json
import pyarrow as pa
from confluent_kafka import Consumer
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType

catalog = load_catalog(
    "default",
    **{
        "type": "sql",
        "uri": "sqlite:///iceberg_catalog.db",
        "warehouse": "./warehouse"
    }
)

if "my_db" not in catalog.list_namespaces():
    catalog.create_namespace("my_db")

try:
    table = catalog.load_table("my_db.my_table")
except:
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=IntegerType(), required=True),
        NestedField(field_id=2, name="data", field_type=StringType(), required=False),
    )
    table = catalog.create_table("my_db.my_table", schema=schema)

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-python-consumer',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['my_topic'])

print("Consumer запущен и ждет сообщения...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue
        
        raw_data = json.loads(msg.value().decode('utf-8'))
        
        arrow_table = pa.Table.from_pylist([raw_data])
        
        table.append(arrow_table)
        print(f"Записано в Iceberg: {raw_data}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()