# Ledgerline business context

## The reference problem

Ledgerline models a common data-engineering problem in multi-channel retail: operational
systems publish events, while finance and operations need reconciled, explainable numbers.
The failure is rarely a lack of dashboards. It is that orders, payments, refunds, inventory
adjustments, and reporting definitions are assembled from systems with different timing,
identifiers, and assumptions.

The target question is deliberately simple:

> Can a stakeholder trace a reported number back to the event history and understand why
> it changed?

## Users and decisions

| User | Decision supported | What must be trusted |
| --- | --- | --- |
| Finance | Can daily revenue be closed and explained? | Order, payment, refund, and recognition logic reconcile. |
| Operations | Is inventory movement complete and current? | Late or missing source data is visible before planning. |
| Product or commercial team | Which channel or product drives outcome? | Metric definitions are stable and documented. |
| Data engineering | Can an incident be recovered without corrupting reporting? | Ingestion is observable, repeatable, and safe to rerun. |

## Implemented version-1 contract

Ledgerline currently emits synthetic, non-sensitive events. Each carries an immutable
source event identifier, event type, contract version, event occurrence time, source
system, correlation key, and event-specific JSON payload.

| Event | Business grain | Purpose |
| --- | --- | --- |
| order_created | One order | Records the commercial intent. |
| payment_captured | One payment transaction | Records cash collection. |
| refund_issued | One refund transaction | Reverses part or all of an earlier payment. |
| inventory_adjusted | One stock movement | Records a quantity adjustment. |

The consumer validates each event against JSON Schema before it reaches Iceberg. Invalid
events are retained in a dead-letter topic with the validation reason and Kafka location.

## Current metrics

| Metric | Grain | Owner | Implemented control |
| --- | --- | --- | --- |
| Event volume | Business date | Data engineering | Source event deduplication and daily-metrics consistency test. |
| Net captured cash | Business date | Finance | Captured payments minus issued refunds. |
| Synthetic recognised revenue | Business date | Finance | Created orders minus issued refunds. |
| Daily reconciliation variance | Business date | Finance | Net cash minus recognised revenue; a non-zero variance fails the dbt test. |
| Inventory adjustment quantity | Product and location event | Operations | Typed inventory event payload and immutable source identifier. |

The reconciliation mart uses a deliberately narrow demo rule. It is not a claim that the
same rule covers real revenue recognition, taxes, partial fulfilment, chargebacks, or
multi-currency accounting.

## Contract and data-product principles

1. **Source event identifiers are immutable.** They are the basis for deduplication,
   replay, and incident investigation.
2. **Event time and ingestion time have different meanings.** The platform stores both so
   late-arrival handling can be measured rather than hidden.
3. **Contract versions are explicit.** The consumer accepts schema version 1 only; a
   breaking change must introduce a reviewed new version.
4. **Duplicate delivery is expected.** The raw event log is at-least-once; transformed
   facts retain one record per source event identifier.
5. **Synthetic data stays synthetic.** No client data, production identifiers, or
   confidential business rules belong in this repository.
6. **A passing pipeline is not the same as a reconciled report.** Technical health and
   business validity are separate controls.

## Ownership

| Artefact | Proposed owner | Change expectation |
| --- | --- | --- |
| Event schema | Source system and data engineering | Versioned, reviewed change. |
| Staging model | Data engineering | Backward-compatible where possible. |
| Finance mart | Data engineering with finance approval | Metric definition changes require review. |
| Data-quality thresholds | Data engineering and domain owner | Reviewed when business process changes. |
| Incident runbook | Data engineering | Updated after material incidents or recovery changes. |

## Deliberate boundaries

This repository is a local-first reference platform. It does not process real customer
data or claim a production cloud deployment. A production adaptation would add source
freshness objectives, secret management, access controls, encryption, a batch audit table,
and domain-approved revenue-recognition rules.