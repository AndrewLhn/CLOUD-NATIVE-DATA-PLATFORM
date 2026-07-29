with source_events as (
    select
        cast(id as bigint) as event_id,
        trim(data) as event_payload,
        event_id as source_event_id,
        cast(kafka_partition as integer) as kafka_partition,
        cast(kafka_offset as bigint) as kafka_offset,
        from_iso8601_timestamp(ingested_at) as ingested_at
    from {{ source('raw', 'kafka_events') }}
),
deduplicated_events as (
    select
        *,
        row_number() over (
            partition by source_event_id
            order by kafka_partition desc, kafka_offset desc
        ) as row_number
    from source_events
)

select
    event_id,
    event_payload,
    source_event_id,
    kafka_partition,
    kafka_offset,
    ingested_at,
    md5(concat(cast(event_id as varchar), '|', event_payload)) as event_hash
from deduplicated_events
where row_number = 1
