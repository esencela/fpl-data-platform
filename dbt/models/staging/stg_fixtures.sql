{{ config(materialized='view') }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select raw_data
    from {{ source('raw', 'fixtures') }}
    order by fetched_at desc
    limit 1
),

source_data as (
    select jsonb_array_elements(raw_data) as fixture
    from latest_snapshot
)

select
    (fixture->>'code')::int as fixture_id,
    (fixture->>'id')::int as fixture_season_id,
    (fixture->>'event')::int as gameweek_id,
    (fixture->>'kickoff_time')::timestamptz as kickoff_time,    
    (fixture->>'finished')::boolean as finished,
    (fixture->>'team_h')::int as home_season_team_id,
    (fixture->>'team_h_score')::int as home_team_score,
    (fixture->>'team_a')::int as away_season_team_id,
    (fixture->>'team_a_score')::int as away_team_score,
    (fixture->>'team_h_difficulty')::int as home_team_difficulty,
    (fixture->>'team_a_difficulty')::int as away_team_difficulty
from source_data