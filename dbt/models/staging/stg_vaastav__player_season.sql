{{ config(
    alias='vaastav_player_season',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest as (
    select 
        raw_data,
        player_season_id,
        season
    from {{ source('raw', 'vaastav_players') }}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'vaastav_players') }})
)

select
    -- Identifiers
    (raw_data->>'code')::int as player_id,
    season::int as season,
    player_season_id::int as player_season_id,
    (raw_data->>'team_code')::int as team_id,
    (raw_data->>'team')::int as team_season_id,

    -- Personal info
    raw_data->>'first_name' as first_name,
    raw_data->>'second_name' as second_name,
    raw_data->>'web_name' as web_name,
    CASE
        WHEN raw_data->>'known_name' = '' THEN NULL
        ELSE raw_data->>'known_name'
    END as known_name,
    ((raw_data->>'region')::numeric)::int as country_id,
    (raw_data->>'birth_date')::date as birth_date,

    -- FPL info
    CASE
        WHEN (raw_data->>'element_type')::int = 1 THEN 'GKP'
        WHEN (raw_data->>'element_type')::int = 2 THEN 'DEF'
        WHEN (raw_data->>'element_type')::int = 3 THEN 'MID'
        WHEN (raw_data->>'element_type')::int = 4 THEN 'FWD'
    END as position,
    (round((raw_data->>'now_cost')::decimal / 10, 1)) as now_cost

from latest