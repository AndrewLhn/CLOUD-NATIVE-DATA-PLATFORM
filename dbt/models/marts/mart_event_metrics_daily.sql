select
    cast(event_occurred_at as date) as metric_date,
    count(*) as event_count,
    count(distinct event_hash) as distinct_payload_count,
    count(distinct source_event_id) as distinct_source_event_count
from {{ ref('fct_kafka_events') }}
group by 1
