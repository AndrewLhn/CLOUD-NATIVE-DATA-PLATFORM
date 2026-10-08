# ADR 002: At-least-once raw ingestion

- Status: Accepted
- Date: 2026-10-08

## Decision

Append valid events to Iceberg, then commit Kafka offsets. Treat the raw layer as
at-least-once and deduplicate transformed facts by source event ID.

## Reason

Kafka and Iceberg do not share one transaction. A crash after the Iceberg append and before
the offset commit can replay records.

## Consequences

Raw duplicates remain available for investigation. dbt keeps one row per source event ID
for analytics and reconciliation.
