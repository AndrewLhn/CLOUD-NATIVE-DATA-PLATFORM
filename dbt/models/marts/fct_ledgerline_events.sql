with parsed_events as (
    select
        *,
        try(json_parse(event_payload)) as event_data
    from {{ ref('fct_kafka_events') }}
)

select
    source_event_id,
    event_type,
    event_occurred_at,
    event_ingested_at,
    source_system,
    correlation_id,
    json_extract_scalar(event_data, '$.order_id') as order_id,
    json_extract_scalar(event_data, '$.payment_id') as payment_id,
    json_extract_scalar(event_data, '$.refund_id') as refund_id,
    json_extract_scalar(event_data, '$.product_id') as product_id,
    json_extract_scalar(event_data, '$.location_id') as location_id,
    json_extract_scalar(event_data, '$.currency') as currency,
    try_cast(json_extract_scalar(event_data, '$.amount') as decimal(18, 2)) as amount,
    try_cast(json_extract_scalar(event_data, '$.quantity_delta') as integer) as quantity_delta,
    event_hash,
    event_payload
from parsed_events
