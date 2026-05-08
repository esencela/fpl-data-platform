{{ config(
    alias='understat_players',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select
        raw_data,
        season
    from {{ source('raw', 'understat_season_data')}}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'understat_season_data') }})
),

source_data as (
    select
        season,
        jsonb_array_elements(raw_data->'players') as player_data
    from latest_snapshot
),

players as (
    select
        season::int as season,
        (player_data->>'id')::int as player_id,
        replace(player_data->>'player_name', '&#039;', '''') as player_name, -- Replace html escape for apostrophe
        player_data->>'team_title' as team_name
    from source_data
)

select
    season,
    player_id,
    player_name,
    team_name
    
from players