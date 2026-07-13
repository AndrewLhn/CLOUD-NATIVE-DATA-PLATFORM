import subprocess
import sys
import os

def install_dependencies():
    packages = ["pyiceberg[sql-sqlite]", "sqlalchemy>=2.0.18"]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)

install_dependencies()

import json
import pyarrow as pa
from confluent_kafka import Consumer
from pyiceberg.catalog import load_catalog

def process_batch():
    catalog = load_catalog("default", **{
        "type": "sql",
        "uri": "sqlite:////tmp/iceberg_catalog.db",
        "warehouse": "s3://warehouse",
        "s3.endpoint": "http://minio:9000",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin"
    })
    
    table = catalog.load_table("my_db.my_table")
    
    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092', 
        'group.id': 'my-python-consumer', 
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['my_topic'])
    
    print("Начинаю чтение из Kafka...")
    
    batch = []
    for _ in range(100):
        msg = consumer.poll(1.0)
        if msg is None:
            break
        if msg.error():
            print(f"Ошибка Kafka: {msg.error()}")
            continue
        batch.append(json.loads(msg.value().decode('utf-8')))
    
    if batch:
        arrow_table = pa.Table.from_pylist(batch)
        table.append(arrow_table)
        print(f"Успешно записано {len(batch)} записей в таблицу Iceberg.")
    else:
        print("Новых сообщений нет.")
        
    consumer.close()

if __name__ == "__main__":
    process_batch()