{{ config(materialized='view') }}

-- Only get data from latest fetch
with latest_snapshot as (
    select
        season,
        fixture_season_id,
        raw_data,
        fetched_at
    from {{ source('raw', 'vaastav_fixtures') }}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'vaastav_fixtures') }})
)

select
    -- Fixture identifiers
    (raw_data->>'code')::int as fixture_id,    
    season::int as season,
    fixture_season_id::int as fixture_season_id,

    -- Fixture info
    (raw_data->>'event')::int as gameweek_id,
    (raw_data->>'kickoff_time')::timestamptz as kickoff_time,    
    (raw_data->>'finished')::boolean as finished,

    -- Team info
    (raw_data->>'team_h')::int as home_team_season_id,
    (raw_data->>'team_h_score')::int as home_team_score,
    (raw_data->>'team_a')::int as away_team_season_id,
    (raw_data->>'team_a_score')::int as away_team_score,
    (raw_data->>'team_h_difficulty')::int as home_team_difficulty,
    (raw_data->>'team_a_difficulty')::int as away_team_difficulty

from latest_snapshot