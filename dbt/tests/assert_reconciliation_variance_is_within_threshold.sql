select *
from {{ ref('mart_daily_reconciliation') }}
where reconciliation_status <> 'passed'
   or abs(variance_amount) > cast(0.01 as decimal(18, 2))
