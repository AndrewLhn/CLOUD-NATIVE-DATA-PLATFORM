#!/usr/bin/env bash
set -euo pipefail

compose=(docker compose)

query_scalar() {
  "${compose[@]}" exec -T trino trino --output-format CSV_HEADER --execute "$1" | tail -n 1 | tr -d "\r"
}

"${compose[@]}" up -d --build --wait
python3 infra/producer.py --scenario ledgerline
python3 infra/producer.py --scenario duplicate
python3 infra/producer.py --scenario invalid
"${compose[@]}" exec -T airflow-standalone airflow dags test kafka_to_iceberg 2026-01-01
"${compose[@]}" --profile tools run --rm dbt build

raw_count="$(query_scalar "SELECT count(*) FROM iceberg.ledgerline_raw.events")"
[[ "$raw_count" == "5" ]]

fact_count="$(query_scalar "SELECT count(*) FROM iceberg.analytics.fct_kafka_events")"
[[ "$fact_count" == "4" ]]

reconciliation_status="$(query_scalar "SELECT reconciliation_status FROM iceberg.analytics.mart_daily_reconciliation")"
[[ "$reconciliation_status" == "passed" ]]

dlq_message="$("${compose[@]}" exec -T kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ledgerline_events_dlq --from-beginning --max-messages 1 --timeout-ms 10000)"
grep -q '"error"' <<<"$dlq_message"
