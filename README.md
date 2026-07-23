# Cloud-native data platform

Local development stack: Kafka → Airflow → Apache Iceberg → MinIO, queried with Trino.

## Start

```bash
cp .env.example .env
docker compose up -d --build
```

Endpoints: Airflow `http://localhost:8080`, MinIO Console `http://localhost:9001`, Trino `http://localhost:8082`, Kafka `localhost:9092`.

The `iceberg-db-init` service creates the dedicated `iceberg_metadata` database. Airflow and Trino use that same PostgreSQL JDBC catalog and the same `s3://warehouse/` path in MinIO.

## Test the pipeline

```bash
python3 infra/producer.py
docker compose exec airflow-standalone airflow dags trigger kafka_to_iceberg
```

Use a Trino client to run:

```sql
SELECT * FROM iceberg.my_db.my_table;
```

## Configuration

Copy `.env.example` to `.env` and replace the development credentials before exposing the stack. `.env` is intentionally ignored by Git.

Terraform under `infra/` is legacy and must not be applied together with this Compose stack: it provisions containers with overlapping names and ports.
