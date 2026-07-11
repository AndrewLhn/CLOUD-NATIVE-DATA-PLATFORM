from confluent_kafka import Producer
import json

p = Producer({'bootstrap.servers': '127.0.0.1:9092'})

data = {"id": 1, "data": "hello world from python"}
p.produce('my_topic', json.dumps(data).encode('utf-8'))
p.flush()

print("Сообщение успешно отправлено в Kafka!")