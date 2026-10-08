# Ledgerline

> A production-inspired event-lakehouse reference platform for trustworthy operational analytics.

**Ledgerline** is the portfolio name for this repository. The GitHub repository remains
CLOUD-NATIVE-DATA-PLATFORM until a separate rename is approved.

The reference business case is a multi-channel retailer that needs a traceable, reliable
path from operational events to analytics. Finance, operations, and product teams should
be able to answer a basic question with confidence: *where did this number come from, and
can the pipeline be safely rerun when the source is late or wrong?*

~~~text
Versioned Ledgerline events → Kafka → Airflow batch ingestion → Apache Iceberg on MinIO
                                                                                 ↓
                                                                        Trino + dbt
                                                                                 ↓
                                           finance-ready facts, daily metrics, reconciliation
~~~

It is deliberately local-first and reproducible. The stack runs with Docker Compose and
does not require a cloud account.

## What is implemented

- A versioned JSON Schema contract for synthetic order, payment, refund, and inventory events.
- Runtime contract validation; invalid messages are sent to a Kafka dead-letter topic.
- An Airflow DAG that consumes batches with retries and an execution timeout.
- Immutable Iceberg storage backed by MinIO, queried through Trino.
- dbt staging, idempotent event facts, payload deduplication, daily metrics, and a daily
  payment-to-revenue reconciliation mart.
- Unit tests for contract validation and producer scenarios.
- A full-stack E2E scenario covering a duplicate event, an invalid event, DLQ routing, and
  a passing daily reconciliation.
- Docker Compose, CI validation, Ruff linting, and a separate end-to-end workflow.
- A small Terraform prototype retained for reference only; it is **not** a supported deployment path.

See [the architecture](docs/architecture.md) for component responsibilities and operational
properties, and [the business context](docs/business-context.md) for metric scope and
ownership.

## Engineering principles

| Principle | How it is applied |
| --- | --- |
| Versioned contracts | Every event declares its type, schema version, occurrence time, source system, and correlation key. |
| Replayability | Raw events are persisted in Iceberg; transformations can be rebuilt from stored data. |
| At-least-once ingestion | Raw duplicates are possible after replay; dbt retains one fact per source event identifier. |
| Data quality | Contract validation, dbt tests, unit tests, CI, and E2E protect separate failure modes. |
| Reconciliation | Net captured cash is compared with synthetic recognised revenue for every business date. |
| Honest scope | The reference platform does not claim production deployment or real customer data. |

## Architecture

~~~mermaid
flowchart LR
    P[Versioned event producer] --> K[Kafka]
    C[JSON Schema validation] -. validates .-> P
    K --> A[Airflow batch DAG]
    A --> DLQ[Kafka dead-letter topic]
    A --> I[Iceberg raw events]
    I --> O[MinIO object storage]
    I --> T[Trino]
    T --> D[dbt]
    D --> F[Event facts and reconciliation mart]
    Q[Unit tests, dbt tests, CI, E2E] -. validates .-> D
~~~

For component responsibilities, reliability properties, and failure modes, read
[docs/architecture.md](docs/architecture.md).

## Quick start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+

Install the small host-side dependency set used by the producer and unit tests:

~~~bash
python3 -m pip install -r requirements.txt
~~~

### Start the stack

~~~bash
cp .env.example .env
docker compose up -d --build
~~~

Local endpoints:

| Service | Address |
| --- | --- |
| Airflow | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| Trino | http://localhost:8082 |
| Kafka | localhost:9092 |

### Exercise the Ledgerline scenario

Publish a reconciled order, payment, refund, and inventory scenario, then trigger the
ingestion DAG:

~~~bash
python3 infra/producer.py --scenario ledgerline
docker compose exec airflow-standalone airflow dags trigger kafka_to_iceberg
~~~

Build transformations and run the quality checks:

~~~bash
make dbt-build
make dbt-test
~~~

Inspect the finance mart through Trino:

~~~sql
SELECT *
FROM iceberg.analytics.mart_daily_reconciliation;
~~~

The sample scenario produces EUR 100.00 of orders, EUR 100.00 of captured payments, and
EUR 20.00 of refunds. It therefore reconciles EUR 80.00 of net cash with EUR 80.00 of
synthetic recognised revenue.

### Demonstrate failure handling

~~~bash
python3 infra/producer.py --scenario duplicate
python3 infra/producer.py --scenario invalid
~~~

The duplicate reuses an existing source event identifier and is removed by the dbt
idempotency rule. The invalid payload is rejected by the JSON Schema validator and sent
to the ledgerline_events_dlq topic.

## Validation

Run the local quality suite before opening a pull request:

~~~bash
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
make validate
make lint
~~~

GitHub Actions runs configuration validation, Python compilation, contract unit tests,
a producer import check, and Ruff on every pull request and push to main. The separate
end-to-end workflow exercises the full Compose stack and saves Compose logs as an artifact
when it fails.

## Data model and quality controls

| Layer | Model | Purpose |
| --- | --- | --- |
| Staging | stg_kafka_events | Types envelope metadata, preserves event and ingestion time, and retains one record per source event identifier. |
| Mart | dim_event_payloads | Deduplicates payload content by hash. |
| Mart | fct_kafka_events | Provides analytics-ready, deduplicated event facts. |
| Mart | fct_ledgerline_events | Parses order, payment, refund, and inventory fields from the event payload. |
| Mart | mart_event_metrics_daily | Tracks event volume and source-event cardinality by business date. |
| Mart | mart_daily_reconciliation | Compares net captured cash with recognised revenue and emits passed or failed status. |

Quality controls cover contract conformance, source event uniqueness, accepted event types,
valid timestamps, fact-to-dimension relationships, financial event completeness, duplicate
handling, DLQ routing, and reconciliation variance.

## Operational documentation

- [Architecture and operational properties](docs/architecture.md)
- [Business context and metric direction](docs/business-context.md)
- [ADR 001 — local-first reference architecture](docs/adr/001-local-first-reference-architecture.md)
- [ADR 002 — event idempotency and late data](docs/adr/002-event-idempotency-and-late-data.md)
- [ADR 003 — data quality as a deployment gate](docs/adr/003-data-quality-as-a-deployment-gate.md)
- [Data-quality incident runbook](docs/runbooks/data-quality-incident.md)

## Configuration and safety

Copy .env.example to .env and use only local development credentials. Do not commit
environment files, Terraform state, local Airflow logs, dbt build artefacts, generated
warehouse data, or Docker runtime data. The repository .gitignore is intentionally
configured to exclude them from future commits.

## Roadmap

The next valuable extension is an ingestion audit table recording DAG run, Kafka
partition/offset range, accepted and rejected record counts, and batch status. That will
make replay, operational metrics, and incident investigation visible in the warehouse
rather than only in logs.