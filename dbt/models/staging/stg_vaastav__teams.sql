{{ config(
    alias='vaastav_teams',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select 
        season,
        team_season_id,
        raw_data
    from {{ source('raw', 'vaastav_teams') }}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'vaastav_teams') }})
)

select 
    -- Team identifiers
    (raw_data->>'code')::int as team_id,
    season::int as season,
    team_season_id::int as team_season_id,

    -- Team names
    raw_data->>'name' as name,
    raw_data->>'short_name' as short_name,

    -- Team strength metrics
    (raw_data->>'strength_overall_home')::int as strength_overall_home,
    (raw_data->>'strength_overall_away')::int as strength_overall_away,
    (raw_data->>'strength_attack_home')::int as strength_attack_home,
    (raw_data->>'strength_attack_away')::int as strength_attack_away,
    (raw_data->>'strength_defence_home')::int as strength_defence_home,
    (raw_data->>'strength_defence_away')::int as strength_defence_away
    
from latest_snapshot