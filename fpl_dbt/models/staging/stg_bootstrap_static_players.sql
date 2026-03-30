{{ config(materialized='view') }}

with source_data as (
    select jsonb_array_elements(raw_data->'elements') as element
    from {{ source('raw', 'bootstrap_static') }}
)

select
    (element->>'code')::int as player_id,
    (element->>'id')::int as player_season_id,
    (element->>'team_code')::int as team_id,
    (element->>'team')::int as season_team_id,
    element->>'first_name' as first_name,
    element->>'second_name' as second_name,
    element->>'web_name' as web_name,
    element->>'known_name' as known_name,
    (element->>'region')::int as country_id,
    (element->>'birth_date')::date as birth_date,
    (element->>'element_type')::int as position_id,
    (round((element->>'now_cost')::decimal / 10, 1)) as now_cost
from source_data
