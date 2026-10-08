# Ledgerline architecture

## Status and purpose

Ledgerline is a production-inspired reference implementation, not a claim that this
repository runs a live customer workload. It demonstrates a locally reproducible event
lakehouse path and the controls a data engineer should design before exposing analytics
to finance, operations, or product users.

The current functional slice implements a synthetic retail domain: order creation, payment
capture, refund issuance, and inventory adjustments. It turns those events into a tested
daily payment-to-revenue reconciliation.

## System context

~~~mermaid
flowchart LR
    Producer[Versioned Ledgerline producer] --> Kafka[Kafka topic]
    Schema[JSON Schema v1] -. validates .-> Consumer
    Kafka --> Consumer[Airflow batch consumer]
    Consumer --> DLQ[Dead-letter topic]
    Consumer --> Iceberg[Iceberg raw events]
    Iceberg --> MinIO[MinIO object storage]
    Iceberg --> Trino[Trino query engine]
    Trino --> dbt[dbt transformation layer]
    dbt --> Marts[Event facts and reconciliation mart]
    Checks[Unit tests, dbt tests, CI, E2E] -. validates .-> Marts
~~~

## Component responsibilities

| Component | Responsibility | Operational note |
| --- | --- | --- |
| Python producer | Emits reproducible valid, duplicate, and invalid Ledgerline scenarios. | It is intentionally a demonstration source, not an external SaaS connector. |
| JSON Schema validator | Rejects unsupported versions and malformed event payloads. | Contract errors are routed to the dead-letter topic. |
| Kafka | Decouples event production from batch ingestion. | A source event identifier is retained for downstream deduplication. |
| Airflow | Schedules and retries the Kafka-to-Iceberg batch. | The DAG has retries and an execution timeout. |
| Iceberg | Stores queryable raw event history. | Raw delivery is at-least-once; raw duplicates are retained as evidence. |
| MinIO | Provides local S3-compatible storage. | It makes the development stack reproducible without cloud credentials. |
| Trino | Queries Iceberg data for transformation and inspection. | dbt uses it as the warehouse adapter. |
| dbt | Builds typed events, domain facts, metrics, and reconciliation output. | Tests are part of the transformation contract. |
| GitHub Actions | Runs unit, static, and end-to-end validation. | The E2E workflow uploads Compose logs when it fails. |

## Data flow

1. The producer sends a version-1 Ledgerline event to Kafka.
2. The Airflow consumer decodes JSON and validates the event against the schema.
3. An invalid event is written to the dead-letter topic with its Kafka offset and reason.
4. A valid event is appended to Iceberg with its source event ID, event time, ingestion
   time, source system, and correlation key.
5. dbt retains one transformed row per source event identifier.
6. dbt parses financial and inventory fields from the payload.
7. The reconciliation mart compares net captured cash with synthetic recognised revenue.
8. A variance outside the threshold fails the dbt build.

## Reliability properties

| Property | Current control | Boundary |
| --- | --- | --- |
| Repeatable local setup | Docker Compose and example environment configuration. | Intended for local development, not multi-region availability. |
| Contract enforcement | JSON Schema validation before Iceberg write and DLQ routing on failure. | The sample supports schema version 1 only. |
| At-least-once delivery | Kafka offsets are committed after the Iceberg append. | A crash in between can duplicate raw records; dbt deduplicates transformed facts. |
| Late-data visibility | Both occurrence and ingestion timestamps are stored. | Explicit late-arrival SLA metrics are the next extension. |
| Quality gate | Contract unit tests, dbt tests, CI, and E2E workflows. | Tests detect defined failure modes; they cannot prove all business semantics. |
| Failure diagnostics | DLQ metadata and E2E Compose-log artifacts. | A production deployment would add alerts and on-call routing. |

## Failure modes and response

| Failure mode | Detection | Initial response |
| --- | --- | --- |
| Invalid event contract | Consumer sends the message to the dead-letter topic. | Inspect the validation error, payload, topic, partition, and offset. |
| Duplicate source event | Raw count exceeds transformed-fact count; dbt fact retains one source event. | Investigate producer retry behaviour; do not erase raw evidence. |
| Batch task failure | Airflow task state and logs show the error. | Review the failed task; correct configuration or data issue; rerun the task. |
| Reconciliation variance | dbt reconciliation test fails. | Stop use of the affected business date; inspect order, payment, and refund events. |
| Full-stack E2E regression | GitHub Actions fails and uploads Compose logs. | Review the artifact before merging or releasing a change. |

See the [data-quality incident runbook](runbooks/data-quality-incident.md) for the detailed
response procedure.

## Deployment boundary

The supported deployment path is local Docker Compose. The Terraform content under infra
is retained as an archived prototype and must not be applied as if it were a supported
production deployment. A cloud deployment would require, at minimum:

- separate development, staging, and production environments;
- secret management instead of local environment files;
- private networking and encryption controls;
- least-privilege identities for ingestion, orchestration, and query workloads;
- data retention, backup, and recovery objectives;
- metrics, alerting, ownership, and incident escalation.

These requirements are intentionally explicit because infrastructure code without an
operational model is not a production platform.