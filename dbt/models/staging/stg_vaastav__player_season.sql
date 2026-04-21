{{ config(
    alias='vaastav_player_season',
    materialized='table'
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
    (raw_data->>'element_type')::int as position,
    (round((raw_data->>'now_cost')::decimal / 10, 1)) as now_cost

from latest