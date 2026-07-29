#!/usr/bin/env bash
set -euo pipefail

compose=(docker compose)

"${compose[@]}" up -d --build --wait
python3 infra/producer.py
"${compose[@]}" exec -T airflow-standalone airflow dags test kafka_to_iceberg 2026-01-01
"${compose[@]}" --profile tools run --rm dbt build
"${compose[@]}" exec -T trino trino --execute \
  'SELECT count(*) AS ingested_events FROM iceberg.my_db.my_table'
