import json
import pyarrow as pa
from confluent_kafka import Consumer
from pyiceberg.catalog import load_catalog

def process_batch(max_messages=100):
    print("Начинаю выполнение процесса...")
    
    catalog = load_catalog(
        "default",
        **{
            "type": "sql",
            "uri": "sqlite:////tmp/iceberg_catalog.db",
            "warehouse": "s3://warehouse",
            "s3.endpoint": "http://minio_storage:9000", 
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "minioadmin"
        }
    )
    print("Каталог загружен.")
    
    table = catalog.load_table("my_db.my_table")
    print("Таблица найдена.")
    
    consumer = Consumer({
        'bootstrap.servers': 'kafka_broker:29092', 
        'group.id': 'batch-consumer-group', 
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['my_topic'])
    print("Консьюмер Kafka настроен.")
    
    batch = []
    messages_processed = 0
    
    try:
        while messages_processed < max_messages:
            msg = consumer.poll(1.0)
            if msg is None: 
                break
            if msg.error(): 
                print(f"Ошибка Kafka: {msg.error()}")
                continue
            
            data = json.loads(msg.value().decode('utf-8'))
            batch.append(data)
            messages_processed += 1
        
        if batch:
            print(f"Подготовка {len(batch)} сообщений для записи...")
            arrow_table = pa.Table.from_pylist(batch)
            table.append(arrow_table)
            print(f"Успешно записано {len(batch)} сообщений в Iceberg.")
        else:
            print("Сообщений для записи не найдено.")
            
    except Exception as e:
        print(f"Критическая ошибка при обработке: {e}")
        raise
    finally:
        consumer.close()
        print("Консьюмер Kafka закрыт.")

if __name__ == "__main__":
    process_batch()