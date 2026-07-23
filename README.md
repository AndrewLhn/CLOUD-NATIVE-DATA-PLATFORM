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

Copy `.env.example` to `.env` and replace the example credentials before exposing the stack. The local `.env` uses conventional development credentials and is intentionally ignored by Git.

## Quality gates

Install local quality tools with `python3 -m pip install -r requirements-dev.txt`, then run `make validate` and `make lint` before committing. CI runs the same Compose and Python checks plus Ruff on every pull request and push to `main`.

Terraform under `infra/` is legacy and must not be applied together with this Compose stack: it provisions containers with overlapping names and ports.
