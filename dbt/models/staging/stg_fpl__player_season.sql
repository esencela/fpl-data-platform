{{ config(materialized='view') }}

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
    CASE
        WHEN element->>'known_name' = '' THEN null
        ELSE element->>'known_name'
    END as known_name,
    (element->>'region')::int as country_id,
    (element->>'birth_date')::date as birth_date,

    -- FPL info
    CASE
        WHEN (element->>'element_type')::int = 1 THEN 'GKP'
        WHEN (element->>'element_type')::int = 2 THEN 'DEF'
        WHEN (element->>'element_type')::int = 3 THEN 'MID'
        WHEN (element->>'element_type')::int = 4 THEN 'FWD'
    END as position_id,
    (round((element->>'now_cost')::decimal / 10, 1)) as now_cost
    
from source_data
