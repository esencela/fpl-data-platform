{{ config(
    alias='fpl_fixtures',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select 
        raw_data,
        season
    from {{ source('raw', 'fpl_fixtures') }}
    order by fetched_at desc
    limit 1
),

source_data as (
    select 
        jsonb_array_elements(raw_data) as fixture,
        season
    from latest_snapshot
)

select
    -- Fixture identifiers
    (fixture->>'code')::int as fixture_id,
    season::int as season,
    (fixture->>'id')::int as fixture_season_id,

    -- Fixture info
    (fixture->>'event')::int as gameweek_id,
    (fixture->>'kickoff_time')::timestamptz as kickoff_time,    
    (fixture->>'finished')::boolean as finished,

    -- Team info
    (fixture->>'team_h')::int as home_team_season_id,
    (fixture->>'team_h_score')::int as home_team_score,
    (fixture->>'team_a')::int as away_team_season_id,
    (fixture->>'team_a_score')::int as away_team_score,
    (fixture->>'team_h_difficulty')::int as home_team_difficulty,
    (fixture->>'team_a_difficulty')::int as away_team_difficulty

from source_data