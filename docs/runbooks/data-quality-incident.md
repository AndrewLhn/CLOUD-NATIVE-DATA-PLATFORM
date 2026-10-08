# Runbook: data-quality incident

## Purpose

Use this runbook when a dbt quality check, CI validation, or end-to-end pipeline run
fails. The goal is to prevent unverified data from being treated as a trustworthy
analytics output, while restoring service through a controlled and repeatable path.

## Triage

1. Record the failing workflow, DAG run, model, test, and source event identifiers.
2. Determine whether the failure blocks a local demonstration, a transformation build,
   or a downstream metric.
3. Stop using the affected mart as a trusted result until the failure is understood.
4. Do not delete raw events or rewrite source data merely to make a test pass.

## Initial checks

~~~bash
docker compose ps
docker compose logs --tail=200 airflow-standalone
make validate
make dbt-test
~~~

For a GitHub Actions failure, download and inspect the Compose log artifact from the
end-to-end workflow.

## Diagnose by symptom

| Symptom | Likely investigation |
| --- | --- |
| Kafka or producer failure | Confirm Kafka health, topic availability, and producer configuration. |
| Airflow task failure | Inspect task logs, execution timeout, service dependencies, and object-store settings. |
| dbt uniqueness failure | Identify repeated source event identifiers and determine whether the source retried or the deduplication rule changed. |
| dbt relationship failure | Verify that the upstream dimension and fact were built from the same ingestion window. |
| Invalid timestamp or null value | Inspect the raw event and contract assumptions; do not coerce silently without a documented decision. |
| E2E regression | Compare the failing service logs with the most recent passing workflow and reproduce locally. |

## Recovery

1. Correct the root cause in code, configuration, or documented source data.
2. Add or update a test if the incident exposed an untested failure mode.
3. Re-run the affected Airflow task or the local end-to-end command.
4. Rebuild dbt models and run tests.
5. Confirm the expected records and metrics with Trino.
6. Record the change in an ADR or issue when it alters architecture, contract, or metric
   semantics.

## Completion criteria

An incident is resolved only when:

- the direct failure no longer reproduces;
- the relevant validation and dbt tests pass;
- the recovery did not discard raw evidence;
- any changed business rule is documented;
- a follow-up is created for remaining monitoring or contract gaps.

## Escalation boundary

This repository is a local reference platform. A production adaptation would add source
owners, severity levels, a communication channel, freshness objectives, alert routing, and
a defined decision on whether finance or operations may consume stale data.