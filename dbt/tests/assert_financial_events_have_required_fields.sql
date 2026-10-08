select *
from {{ ref('fct_ledgerline_events') }}
where event_type in ('order_created', 'payment_captured', 'refund_issued')
  and (
      order_id is null
      or currency is null
      or amount is null
      or amount <= 0
  )
