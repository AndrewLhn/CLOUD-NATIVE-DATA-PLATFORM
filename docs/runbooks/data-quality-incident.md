# Runbook: data-quality incident

## Triage

1. Record the failed DAG run, dbt model or test, and Kafka topic/partition/offset.
2. Stop using the affected mart until the failure is understood.
3. Keep raw records and DLQ messages; do not delete evidence to make a test pass.

## Checks

~~~bash
docker compose ps
docker compose logs --tail=200 airflow-standalone
make validate
make dbt-test
~~~

For GitHub Actions failures, download the Compose log artifact from the E2E run.

## Common cases

| Symptom | Check |
| --- | --- |
| Invalid event | Inspect the DLQ message and JSON Schema error |
| Duplicate fact | Compare raw source event IDs with stg_kafka_events |
| Airflow failure | Inspect the failed task and service health |
| Reconciliation failure | Compare order, payment, and refund events for the business date |
| E2E failure | Reproduce locally and inspect Compose logs |

## Recovery

1. Correct the source, contract, or transformation issue.
2. Add a test if the failure mode was not covered.
3. Re-run the Airflow task.
4. Run dbt build and dbt test.
5. Verify the affected mart with Trino.

Close the incident only after validation passes and the changed rule is documented.
