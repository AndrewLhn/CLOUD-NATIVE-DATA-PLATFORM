# ADR 003: Treat data quality as a deployment gate

- Status: Accepted
- Date: 2026-10-08

## Context

A successful orchestration run only shows that code executed. It does not show that the
data is unique, complete, referentially consistent, or semantically usable. Analytics
marts should not be treated as trustworthy merely because a task returned success.

The current dbt project already includes generic and singular tests for core properties,
while GitHub Actions validates configuration, Python code, linting, and a full
end-to-end path.

## Decision

dbt tests are part of the build contract. The documented workflow is:

1. ingest or prepare source events;
2. build models;
3. run tests;
4. publish or consume marts only when the relevant checks pass;
5. investigate a failure using the data-quality incident runbook.

CI validates change safety before merge; the E2E workflow validates that the stack works
as an integrated system.

## Consequences

### Positive

- A failed uniqueness or relationship check is visible before it becomes a dashboard
  discrepancy.
- Test definitions live with the models they protect.
- The pull-request workflow exercises both static and runtime validation.
- The project demonstrates that reliability includes data semantics, not only process
  uptime.

### Negative

- Tests add runtime and maintenance cost.
- A green test suite cannot validate business assumptions that were never encoded.
- Threshold-based anomaly detection and source freshness objectives remain future
  extensions for the Ledgerline domain slice.

## Alternatives considered

- Run tests only manually: rejected because it makes quality dependent on memory and
  individual discipline.
- Validate only raw ingestion: rejected because many defects emerge during
  transformation and joins.
- Treat every warning as a hard failure: rejected because production systems need
  explicit severity and escalation policy rather than indiscriminate blocking.