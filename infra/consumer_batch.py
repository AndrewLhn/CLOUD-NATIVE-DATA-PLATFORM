import json
import pyarrow as pa
from confluent_kafka import Consumer, KafkaError
from pyiceberg.catalog import load_catalog

def process_batch(max_messages=100):
    catalog = load_catalog("default", **{"type": "sql", "uri": "sqlite:///iceberg_catalog.db", "warehouse": "s3://warehouse"})
    table = catalog.load_table("my_db.my_table")
    
    consumer = Consumer({'bootstrap.servers': '127.0.0.1:9092', 'group.id': 'my-python-consumer', 'auto.offset.reset': 'earliest'})
    consumer.subscribe(['my_topic'])
    
    batch = []
    messages_processed = 0
    
    while messages_processed < max_messages:
        msg = consumer.poll(1.0)
        if msg is None: break
        if msg.error(): continue
        
        data = json.loads(msg.value().decode('utf-8'))
        batch.append(data)
        messages_processed += 1
    
    if batch:
        arrow_table = pa.Table.from_pylist(batch)
        table.append(arrow_table)
        print(f"Записано {len(batch)} сообщений в Iceberg.")
    
    consumer.close()

if __name__ == "__main__":
    process_batch()