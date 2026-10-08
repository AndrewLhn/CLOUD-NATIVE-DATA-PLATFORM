# Ledgerline

> A production-inspired event-lakehouse reference platform for trustworthy operational analytics.

**Ledgerline** is the portfolio name for this repository. The GitHub repository remains
CLOUD-NATIVE-DATA-PLATFORM until a separate rename is approved.

The reference business case is a multi-channel retailer that needs a traceable, reliable
path from operational events to analytics. Finance, operations, and product teams should
be able to answer a basic question with confidence: *where did this number come from, and
can the pipeline be safely rerun when the source is late or wrong?*

The current implementation is a self-contained event-platform baseline:

~~~text
Kafka events → Airflow batch ingestion → Apache Iceberg on MinIO
                                              ↓
                                      Trino + dbt models
                                              ↓
                           deduplicated event facts and daily metrics
~~~

It is deliberately local-first and reproducible. The stack runs with Docker Compose and
does not require a cloud account.

## What is implemented

- A Python producer publishing JSON events to Kafka.
- An Airflow DAG that consumes batches with retries and an execution timeout.
- Immutable Iceberg storage backed by MinIO, queried through Trino.
- dbt staging, event facts, payload deduplication, daily metrics, and custom data tests.
- JSON Schema documentation for the sample event contract.
- Docker Compose, CI validation, Ruff linting, and a separate end-to-end workflow.
- A small Terraform prototype retained for reference only; it is **not** a supported deployment path.

See [the architecture](docs/architecture.md) for component responsibilities and operational
properties, and [the business context](docs/business-context.md) for the scenario this
platform is designed to model.

## Engineering principles

| Principle | How it is applied |
| --- | --- |
| Reproducibility | One Docker Compose stack, versioned configuration, and automated validation. |
| Replayability | Raw events are persisted in Iceberg; transformations can be rebuilt from stored data. |
| Idempotency | dbt retains one row per source event identifier before marts are built. |
| Data quality | Schema, uniqueness, relationship, completeness, and daily-metric checks run with dbt. |
| Operability | Airflow retries and timeouts, CI/E2E checks, and a documented incident response path. |
| Honest scope | The reference platform does not claim production deployment or real customer data. |

## Architecture

~~~mermaid
flowchart LR
    P[Python event producer] --> K[Kafka]
    K --> A[Airflow batch DAG]
    A --> I[Apache Iceberg]
    I --> O[MinIO object storage]
    I --> T[Trino]
    T --> D[dbt]
    D --> F[Event fact and daily metrics marts]
    C[JSON event contract] -. documents .-> K
    Q[dbt tests and CI/E2E] -. validates .-> D
~~~

For a component-by-component explanation, failure modes, and the next domain extension,
read [docs/architecture.md](docs/architecture.md).

## Quick start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ for local validation commands
- Optional: a Trino client for ad-hoc queries

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

The iceberg-db-init service creates the dedicated iceberg_metadata database.
Airflow and Trino use the same PostgreSQL JDBC catalog and the same s3://warehouse/
location in MinIO.

### Exercise the pipeline

Publish a sample event, then trigger the ingestion DAG:

~~~bash
python3 infra/producer.py
docker compose exec airflow-standalone airflow dags trigger kafka_to_iceberg
~~~

After the DAG completes, use a Trino client to inspect the raw Iceberg table:

~~~sql
SELECT *
FROM iceberg.my_db.my_table;
~~~

Build transformations and run the quality checks:

~~~bash
make dbt-build
make dbt-test
~~~

The dbt service is in the optional tools Compose profile, so it runs only when invoked.

## Validation

Run the local checks before opening a pull request:

~~~bash
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
make validate
make lint
~~~

GitHub Actions runs configuration validation, Python compilation, a producer import check,
and Ruff on every pull request and push to main. The separate end-to-end workflow starts
the full Compose stack and saves Compose logs as an artifact if it fails.

## Data model and quality controls

The current dbt layer creates:

| Layer | Model | Purpose |
| --- | --- | --- |
| Staging | stg_kafka_events | Normalises source fields and retains one record per source event identifier. |
| Mart | dim_event_payloads | Deduplicates payload content by hash. |
| Mart | fct_kafka_events | Provides analytics-ready event facts. |
| Mart | mart_event_metrics_daily | Tracks daily event volume and payload cardinality. |

Quality checks cover source event uniqueness, non-nullness, positive identifiers,
relationships between facts and dimensions, and valid transformed timestamps. The full
contract and ownership direction are documented in
[docs/business-context.md](docs/business-context.md).

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

The next product-facing slice of Ledgerline is a domain contract for order_created,
payment_captured, refund_issued, and inventory_adjusted events. It will add
finance-oriented marts and daily reconciliation between operational orders, payments, and
recognised revenue. This scope is planned, not represented as already implemented.
