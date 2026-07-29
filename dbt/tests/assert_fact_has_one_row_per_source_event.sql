select
    source_event_id
from {{ ref('fct_kafka_events') }}
group by source_event_id
having count(*) > 1
