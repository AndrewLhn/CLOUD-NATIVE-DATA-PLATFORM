select fact.event_hash
from {{ ref('fct_kafka_events') }} as fact
left join {{ ref('dim_event_payloads') }} as dimension
    on fact.event_hash = dimension.event_hash
where dimension.event_hash is null
