with source_events as (
    select
        cast(id as bigint) as event_id,
        trim(data) as event_payload
    from {{ source('raw', 'kafka_events') }}
)

select
    event_id,
    event_payload,
    md5(concat(cast(event_id as varchar), '|', event_payload)) as event_hash
from source_events
