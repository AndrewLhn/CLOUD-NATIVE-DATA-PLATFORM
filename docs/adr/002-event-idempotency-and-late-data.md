# ADR 002: Use source event identity for idempotency; model late data explicitly

- Status: Accepted for the current baseline
- Date: 2026-10-08

## Context

Event systems experience retries, duplicate delivery, and late arrival. A data platform
that treats every received message as a new business fact will inflate reporting and make
backfills unsafe.

The current sample contract contains a source event UUID. The dbt staging layer uses that
identifier to retain one record per source event before marts are built.

## Decision

The source event identifier is the current idempotency key. The staging model selects one
row per identifier before downstream fact and metric models are materialised.

The next domain contract will preserve both event occurrence time and ingestion time.
Late-arriving events will be measured by comparing these two timestamps and handled by
an explicit backfill or incremental-window policy. They will not be silently reassigned
to the time at which the platform received them.

## Consequences

### Positive

- Retried messages do not create duplicate transformed facts.
- Source identity gives incident responders a concrete investigation key.
- Reprocessing remains possible when source data or transformation rules change.
- The eventual finance domain can distinguish a late operational event from a late
  reporting process.

### Negative

- The raw ingestion layer must preserve the source event identifier reliably.
- Deduplication policy needs a documented ordering rule when duplicate messages differ.
- The current generic slice does not yet expose a complete late-arrival metric; that is a
  stated extension, not a hidden assumption.

## Alternatives considered

- Deduplicate only by payload hash: rejected because legitimate repeated business actions
  may have identical payload content.
- Deduplicate by Kafka offset: rejected because offsets are transport-specific and do not
  survive replay or topic migration.
- Drop all late events: rejected because it produces reporting that is stable but wrong.