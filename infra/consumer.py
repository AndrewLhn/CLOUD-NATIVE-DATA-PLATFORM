from confluent_kafka import Consumer
from pyiceberg.catalog import load_catalog
import json

catalog = load_catalog("default", **{
    "uri": "thrift://localhost:9083", 
    "warehouse": "s3://my-warehouse"
})
table = catalog.load_table("my_db.my_table")

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-python-consumer',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['my_topic'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        
        data = json.loads(msg.value().decode('utf-8'))
        
        # Запись в Iceberg
        table.append(data)
        print(f"Записано: {data}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()