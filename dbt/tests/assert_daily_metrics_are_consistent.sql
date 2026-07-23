select *
from {{ ref('mart_event_metrics_daily') }}
where distinct_payload_count > event_count
