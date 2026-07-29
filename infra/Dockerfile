FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY infra/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY infra/consumer.py ./infra/consumer.py
COPY dags/kafka_to_iceberg_run.py ./dags/kafka_to_iceberg_run.py

CMD ["python", "infra/consumer.py"]
