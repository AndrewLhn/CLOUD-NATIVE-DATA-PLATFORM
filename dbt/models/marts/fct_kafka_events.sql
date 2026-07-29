select
    event_id,
    source_event_id,
    event_hash,
    event_payload,
    kafka_partition,
    kafka_offset,
    ingested_at,
    current_timestamp as transformed_at
from {{ ref('stg_kafka_events') }}
