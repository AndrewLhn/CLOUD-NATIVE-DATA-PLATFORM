import json
import socket
import pyarrow as pa
from confluent_kafka import Consumer, KafkaError
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType

# --- Патч для принудительного IPv4 ---
original_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # Если просят localhost, отдаем строго IPv4 127.0.0.1
    if host == 'localhost':
        return original_getaddrinfo('127.0.0.1', port, socket.AF_INET, type, proto, flags)
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = patched_getaddrinfo

# 1. Настройка каталога
catalog = load_catalog(
    "default",
    **{
        "type": "sql",
        "uri": "sqlite:///iceberg_catalog.db",
        "warehouse": "./warehouse"
    }
)

# 2. Инициализация пространства и таблицы
try:
    catalog.create_namespace("my_db")
except Exception:
    pass

try:
    table = catalog.load_table("my_db.my_table")
    print("Таблица загружена.")
except Exception:
    print("Создаем новую таблицу...")
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=IntegerType(), required=True),
        NestedField(field_id=2, name="data", field_type=StringType(), required=False),
    )
    table = catalog.create_table("my_db.my_table", schema=schema)

# 3. Kafka Consumer
# 'broker.address.family': 'v4' — это стандартный способ для librdkafka ограничиться IPv4
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-python-consumer',
    'auto.offset.reset': 'earliest',
    'broker.address.family': 'v4'
})
consumer.subscribe(['my_topic'])

# Схема
arrow_schema = pa.schema([
    ('id', pa.int32()),
    ('data', pa.string())
])

print("Consumer запущен и ждет сообщения...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Ошибка Kafka: {msg.error()}")
                continue
            
        try:
            raw_data = json.loads(msg.value().decode('utf-8'))
            
            if 'id' not in raw_data:
                continue
                
            arrow_table = pa.Table.from_pylist([raw_data], schema=arrow_schema)
            table.append(arrow_table)
            print(f"Успешно записано: {raw_data}")
        except Exception as e:
            print(f"Ошибка обработки: {e}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()