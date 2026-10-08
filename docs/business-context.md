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

## Current implementation

The current repository implements the event-platform baseline, not the full retail
domain model. It contains generic sample events, an event fact, a payload dimension, and a
daily metrics mart. This is sufficient to demonstrate Kafka ingestion, Iceberg storage,
deduplicated modelling, and quality checks.

It does not yet claim to ingest real commerce sources, process personally identifiable
information, calculate recognised revenue, or perform payment reconciliation.

## Planned domain contract

The next domain-focused slice will introduce synthetic, non-sensitive events:

| Event | Business grain | Initial purpose |
| --- | --- | --- |
| order_created | One order | Records the commercial intent. |
| payment_captured | One payment transaction | Records cash collection. |
| refund_issued | One refund transaction | Reverses all or part of an earlier payment. |
| inventory_adjusted | One stock movement | Records a quantity or cost adjustment. |
| product_cost_revised | One product-cost effective period | Supports auditable margin restatement. |

The events will carry immutable source identifiers, occurrence time, ingestion time, and
a versioned payload. This separates source truth from transformation logic and allows
late-arriving events to be measured rather than silently discarded.

## Metric direction

The following metrics are design targets. They are not presented as implemented outputs
until the domain contract and models exist.

| Metric | Proposed grain | Owner | Key control |
| --- | --- | --- | --- |
| Net revenue | Order line or recognised transaction | Finance | Orders, payments, and refunds reconcile. |
| Gross margin | Order line | Finance and commercial | Cost effective date is explicit. |
| Inventory on hand | Product and location snapshot | Operations | Every movement is traceable to a source event. |
| Refund rate | Product, channel, and order cohort | Commercial | Refund remains linked to its original transaction. |
| Daily reconciliation variance | Date and legal entity | Finance | Variance has a threshold, status, and explanation. |

## Data contract principles

1. **Source event identifiers are immutable.** They are the basis for deduplication,
   replay, and incident investigation.
2. **Event time and ingestion time have different meanings.** A late event should not be
   silently treated as if it happened on arrival.
3. **Business definitions are versioned documentation.** A model name alone is not a
   metric definition.
4. **Synthetic data stays synthetic.** No client data, production identifiers, or
   confidential business rules belong in this repository.
5. **A passing pipeline is not the same as a reconciled report.** Technical health and
   business validity are separate controls.

## Ownership

| Artefact | Proposed owner | Change expectation |
| --- | --- | --- |
| Event schema | Source system and data engineering | Versioned, reviewed change. |
| Staging model | Data engineering | Backward-compatible where possible. |
| Finance mart | Data engineering with finance approval | Metric definition changes require review. |
| Data-quality thresholds | Data engineering and domain owner | Reviewed when business process changes. |
| Incident runbook | Data engineering | Updated after material incidents or recovery changes. |

The purpose of this documentation is not to overstate the demo. It makes the gap between
a working technology slice and a trusted business data product visible, planned, and
reviewable.