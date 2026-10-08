# Domain and reconciliation rules

## Events

| Event | Required business fields |
| --- | --- |
| order_created | order_id, customer_id, channel, currency, amount |
| payment_captured | payment_id, order_id, currency, amount |
| refund_issued | refund_id, payment_id, order_id, currency, amount |
| inventory_adjusted | adjustment_id, product_id, location_id, quantity_delta |

The schema accepts version 1 only. Breaking changes require a new version.

## Reconciliation

The current mart operates by business date:

~~~text
net_captured_cash = captured_payment_amount - refunded_amount
recognised_revenue = ordered_amount - refunded_amount
variance_amount = net_captured_cash - recognised_revenue
~~~

A variance above EUR 0.01 sets reconciliation_status to failed and fails the dbt test.

The sample scenario is intentionally small:

~~~text
orders:   EUR 100.00
payments: EUR 100.00
refunds:  EUR  20.00
result:   EUR  80.00 net cash and EUR 80.00 revenue
~~~

## Data rules

- source event IDs are immutable;
- occurrence time and ingestion time are separate fields;
- raw data may contain duplicates after replay;
- transformed facts are deduplicated by source event ID;
- invalid events are retained in the DLQ;
- all data in the repository is synthetic.

## Not modelled

This project does not model tax, partial fulfilment, chargebacks, inventory valuation,
multi-currency conversion, or accounting-grade revenue recognition.
