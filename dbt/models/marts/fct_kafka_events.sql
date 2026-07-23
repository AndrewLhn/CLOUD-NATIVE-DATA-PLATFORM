select
    event_id,
    event_hash,
    event_payload,
    current_timestamp as transformed_at
from {{ ref('stg_kafka_events') }}
