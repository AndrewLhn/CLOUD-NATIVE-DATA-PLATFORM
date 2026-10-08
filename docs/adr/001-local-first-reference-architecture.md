# ADR 001: Keep the supported platform local-first

- Status: Accepted
- Date: 2026-10-08

## Context

The project is a public reference implementation. Its purpose is to demonstrate a
reproducible data-platform design without requiring a cloud account, long-lived
credentials, or paid infrastructure. The stack needs to exercise event ingestion,
orchestration, table storage, SQL transformation, and data-quality checks in one
developer-controlled environment.

A Terraform prototype is present in infra, but it does not constitute an operated cloud
deployment.

## Decision

The supported execution path is Docker Compose with Kafka, Airflow, PostgreSQL, MinIO,
Trino, and dbt. MinIO provides a local S3-compatible storage layer; Iceberg and Trino
preserve the lakehouse interfaces used by many cloud deployments.

Terraform remains archived reference material. It must not be described as a supported
deployment or applied without a separate design, security review, and operational plan.

## Consequences

### Positive

- A reviewer can reproduce the platform without cloud credentials.
- CI can validate the configuration and run an end-to-end path.
- The repository contains no required production account or customer dependency.
- The architecture stays focused on engineering controls rather than provider-specific
  console setup.

### Negative

- It does not demonstrate production networking, managed identity, encryption, or cloud
  cost controls.
- Availability and throughput characteristics of the local stack must not be extrapolated
  to a managed deployment.
- A real cloud deployment remains future work rather than an implied feature.

## Alternatives considered

- Cloud-only AWS deployment: rejected for the supported path because it increases cost,
  credential-management burden, and reviewer setup time.
- Single-process local database: rejected because it would not exercise the event,
  object-storage, and query-engine boundaries central to the reference architecture.