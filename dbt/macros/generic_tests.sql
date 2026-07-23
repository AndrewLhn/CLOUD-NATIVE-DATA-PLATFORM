{% test not_empty_string(model, column_name) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and length(trim(cast({{ column_name }} as varchar))) = 0
{% endtest %}

{% test is_positive(model, column_name) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and {{ column_name }} <= 0
{% endtest %}
