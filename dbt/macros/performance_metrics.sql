{% macro safe_divide(numerator, denominator) %}
    case
        when {{ denominator }} = 0 then 0
        else round({{ numerator }} * 1.0 / {{ denominator }}, 3)
    end
{% endmacro %}