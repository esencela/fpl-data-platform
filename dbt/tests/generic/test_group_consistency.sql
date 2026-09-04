{% test group_consistency(model, column_name, group_by) %}

-- Tests that values of a column are consistent within a group. Test will fail if there are multiple values of the column within a group.
select
    {{ group_by }},
    count(distinct {{ column_name }}) as n_distinct
from {{ model }}
group by {{ group_by }}
having count(distinct {{ column_name }}) > 1

{% endtest %}