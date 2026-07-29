with expected as (
    select
        cast(transformed_at as date) as metric_date,
        count(*) as event_count,
        count(distinct event_hash) as distinct_payload_count
    from {{ ref('fct_kafka_events') }}
    group by 1
)

select
    metrics.metric_date,
    metrics.event_count,
    metrics.distinct_payload_count
from {{ ref('mart_event_metrics_daily') }} as metrics
full outer join expected
    on metrics.metric_date = expected.metric_date
where metrics.event_count is distinct from expected.event_count
   or metrics.distinct_payload_count is distinct from expected.distinct_payload_count
