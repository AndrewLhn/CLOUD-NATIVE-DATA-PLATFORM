select
    event_hash,
    max(event_payload) as event_payload
from {{ ref('stg_kafka_events') }}
group by event_hash
