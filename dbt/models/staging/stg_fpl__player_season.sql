{{ config(
    alias='fpl_player_season',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select 
        raw_data, 
        season
    from {{ source('raw', 'fpl_bootstrap_static') }}
    order by fetched_at desc
    limit 1
),

source_data as (
    select 
        jsonb_array_elements(raw_data->'elements') as element,
        season
    from latest_snapshot
)

select
    -- Identifiers
    (element->>'code')::int as player_id,
    season::int as season,
    (element->>'id')::int as player_season_id,
    (element->>'team_code')::int as team_id,
    (element->>'team')::int as team_season_id,

    -- Personal info
    element->>'first_name' as first_name,
    element->>'second_name' as second_name,
    element->>'web_name' as web_name,
    element->>'known_name' as known_name,
    (element->>'region')::int as country_id,
    (element->>'birth_date')::date as birth_date,

    -- FPL info
    (element->>'element_type')::int as position,
    (round((element->>'now_cost')::decimal / 10, 1)) as now_cost
    
from source_data
