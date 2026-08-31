{% macro create_normalize_player_name_function() %}

create or replace function normalize_player_name(name text)
returns text as $func$
    select
        lower(
            unaccent(
                translate(
                    name,
                    'İIıŞşĞğÖöÜüÇç',
                    'IIiSsGgOoUuCc'
                )
            )
        )
$func$ language sql immutable;
{% endmacro %}