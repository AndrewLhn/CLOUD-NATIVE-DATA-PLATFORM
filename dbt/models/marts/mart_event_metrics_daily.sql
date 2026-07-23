select
    cast(transformed_at as date) as metric_date,
    count(*) as event_count,
    count(distinct event_hash) as distinct_payload_count
from {{ ref('fct_kafka_events') }}
group by 1
