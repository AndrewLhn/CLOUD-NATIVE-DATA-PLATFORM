# ADR 003: Quality checks block reconciliation output

- Status: Accepted
- Date: 2026-10-08

## Decision

Run contract tests, dbt tests, CI checks, and E2E checks as part of the build process.

## Reason

A completed task does not prove that data is valid or reconciled.

## Consequences

Invalid events go to the DLQ. Contract violations, duplicate-handling failures, missing
financial fields, and reconciliation variance fail validation.
