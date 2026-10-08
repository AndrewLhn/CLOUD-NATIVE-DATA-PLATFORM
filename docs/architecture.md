# Ledgerline architecture

## Status and purpose

Ledgerline is a production-inspired reference implementation, not a claim that this
repository runs a live customer workload. It demonstrates a locally reproducible event
lakehouse path and the controls a data engineer should design before exposing analytics
to finance, operations, or product users.

The current functional slice handles generic events. The retail-oriented order, payment,
refund, and inventory vocabulary is documented as the next domain extension in
[Business context](business-context.md).

## System context

~~~mermaid
flowchart LR
    Producer[Python sample producer] --> Kafka[Kafka topic]
    Contract[JSON event contract] -. documents .-> Kafka
    Kafka --> Airflow[Airflow batch DAG]
    Airflow --> Iceberg[Iceberg tables]
    Iceberg --> MinIO[MinIO object storage]
    Iceberg --> Trino[Trino query engine]
    Trino --> dbt[dbt transformation layer]
    dbt --> Marts[Event fact and daily metrics marts]
    Checks[dbt tests, CI, E2E] -. validates .-> Marts
~~~

## Component responsibilities

| Component | Responsibility | Operational note |
| --- | --- | --- |
| Python producer | Emits a reproducible sample event to Kafka. | It is intentionally a demonstration source, not an external SaaS connector. |
| Kafka | Decouples event production from batch ingestion. | A source event identifier is retained for deduplication. |
| Airflow | Schedules and retries the Kafka-to-Iceberg batch. | The DAG has retries and an execution timeout. |
| Iceberg | Stores the queryable event history. | Table storage is object-backed and rebuildable by downstream transformations. |
| MinIO | Provides a local S3-compatible object store. | It makes the development stack reproducible without cloud credentials. |
| Trino | Queries Iceberg data for transformation and inspection. | dbt uses it as the warehouse adapter. |
| dbt | Builds staging, fact, dimension, and daily metric models. | Tests are part of the transformation contract. |
| GitHub Actions | Runs validation, linting, and end-to-end checks. | The E2E workflow uploads Compose logs when it fails. |

## Data flow

1. A source produces a JSON event with a business-independent numeric identifier, payload,
   source event UUID, and occurrence timestamp.
2. Kafka buffers the event until the Airflow batch task consumes it.
3. The Airflow task writes the event data to Iceberg.
4. dbt stages source fields and selects one row per source event identifier.
5. dbt materialises the payload dimension, event fact, and daily metrics mart.
6. Generic and singular tests validate the transformed models before the run is treated as
   successful.

## Reliability properties

| Property | Current control | Boundary |
| --- | --- | ---|
| Repeatable local setup | Docker Compose and example environment configuration. | Intended for local development, not multi-region availability. |
| Pipeline retries | Airflow retries failed batch work three times. | Retry policy is not a replacement for source-level dead-letter handling. |
| Idempotent modelling | The staging model deduplicates by source event identifier. | The raw ingestion writer must preserve the identifier for this to work. |
| Rebuildable transformations | dbt reads persisted Iceberg data. | Raw retention and catalog availability remain dependencies. |
| Quality gate | dbt tests plus CI and E2E workflows. | Tests detect defined failure modes; they cannot prove all business semantics. |
| Failure diagnostics | E2E uploads Compose logs on failure. | A production deployment would add metrics, alerts, and on-call routing. |

## Failure modes and response

| Failure mode | Detection | Initial response |
| --- | --- | --- |
| Kafka is unavailable | Producer or consumer fails; Compose health checks fail. | Confirm service health, restore connectivity, then replay the batch. |
| Batch task fails | Airflow task state and logs show the error. | Review the failed task; correct configuration or data issue; rerun the task. |
| Duplicate source event | dbt uniqueness and fact-level tests fail. | Find the duplicate source event identifier and verify producer behaviour. |
| Invalid transformed record | dbt test fails in the tools profile or CI. | Stop publication of downstream metrics and follow the incident runbook. |
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