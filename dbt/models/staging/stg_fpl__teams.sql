{{ config(
    alias='fpl_teams',
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
        jsonb_array_elements(raw_data->'teams') as team,
        season
    from latest_snapshot
)

select 
    -- Team identifiers
    (team->>'code')::int as team_id,
    season::int as season,
    (team->>'id')::int as team_season_id,

    -- Team names
    team->>'name' as name,
    team->>'short_name' as short_name,

    -- Team strength metrics
    (team->>'strength_overall_home')::int as strength_overall_home,
    (team->>'strength_overall_away')::int as strength_overall_away,
    (team->>'strength_attack_home')::int as strength_attack_home,
    (team->>'strength_attack_away')::int as strength_attack_away,
    (team->>'strength_defence_home')::int as strength_defence_home,
    (team->>'strength_defence_away')::int as strength_defence_away
    
from source_data

