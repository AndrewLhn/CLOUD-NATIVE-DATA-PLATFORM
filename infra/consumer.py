import json
import pyarrow as pa
from confluent_kafka import Consumer, KafkaError
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType

catalog = load_catalog(
    "default",
    **{
        "type": "sql",
        "uri": "sqlite:///iceberg_catalog.db",
        "warehouse": "s3://warehouse",
        "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        "s3.endpoint": "http://127.0.0.1:9000",
        "s3.access-key-id": "minioadmin", 
        "s3.secret-access-key": "minioadmin",
        "s3.path-style-access": "true",
    }
)

namespace = "my_db"
try:
    catalog.create_namespace(namespace)
    print(f"Namespace {namespace} создан.")
except:
    print(f"Namespace {namespace} уже существует.")

try:
    table = catalog.load_table(f"{namespace}.my_table")
    print("Таблица загружена.")
except:
    print("Создаем новую таблицу...")
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=IntegerType(), required=True),
        NestedField(field_id=2, name="data", field_type=StringType(), required=False),
    )
    table = catalog.create_table(f"{namespace}.my_table", schema=schema)

consumer = Consumer({
    'bootstrap.servers': '127.0.0.1:9092',
    'group.id': 'my-python-consumer',
    'auto.offset.reset': 'earliest',
})
consumer.subscribe(['my_topic'])

arrow_schema = pa.schema([
    pa.field('id', pa.int32(), nullable=False),
    pa.field('data', pa.string(), nullable=True)
])

print("Consumer запущен и ждет сообщения...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Ошибка Kafka: {msg.error()}")
            continue
            
        try:
            data = json.loads(msg.value().decode('utf-8'))
            arrow_table = pa.Table.from_pylist([data], schema=arrow_schema)пше 
            table.append(arrow_table)
            print(f"Успешно записано в Iceberg: {data}")
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()