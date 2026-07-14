
def run_sync():
    import json
    import pyarrow as pa
    from confluent_kafka import Consumer
    from pyiceberg.catalog import load_catalog
    from pyiceberg.exceptions import NoSuchTableError

    print("Запуск синхронизации внутри изолированного окружения...")
    
    catalog = load_catalog("default", **{
        "type": "sql",
        "uri": "sqlite:////opt/airflow/iceberg_catalog.db",
        "warehouse": "s3://warehouse",
        "s3.endpoint": "http://minio:9000",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin"
    })

    try:
        catalog.create_namespace("my_db")
    except Exception:
        pass

    schema = pa.schema([
        ("id", pa.int64()),
        ("name", pa.string()),
    ])

    try:
        table = catalog.load_table("my_db.my_table")
    except NoSuchTableError:
        table = catalog.create_table("my_db.my_table", schema=schema)
        print("Таблица my_db.my_table успешно создана.")

    consumer = Consumer({
        'bootstrap.servers': 'kafka:29092', 
        'group.id': 'airflow-consumer-group', 
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['my_topic'])
    
    batch = []
    print("Ожидание сообщений из Kafka...")
    
    for _ in range(10):
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
        print(f"Успешно записано {len(batch)} сообщений в Iceberg.")
    else:
        print("Новых сообщений в Kafka не обнаружено.")
        
    consumer.close()

if __name__ == "__main__":
    run_sync()