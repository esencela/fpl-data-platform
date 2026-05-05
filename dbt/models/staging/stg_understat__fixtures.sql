{{ config(
    alias='understat_fixtures',
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
        jsonb_array_elements(raw_data->'dates') as fixture_data
    from latest_snapshot
)

select 
    -- Identifiers
    (fixture_data->>'id')::int as fixture_id,
    season::int as season,

    -- Fixture info
    (fixture_data->>'datetime')::timestamp as kickoff_time,
    (fixture_data->>'isResult')::boolean as finished,

    -- Team info
    (fixture_data->'h'->>'id')::int as home_team_id,
    (fixture_data->'goals'->>'h')::int as home_team_score,
    (fixture_data->'a'->>'id')::int as away_team_id,
    (fixture_data->'goals'->>'a')::int as away_team_score,
    (fixture_data->'xG'->>'h')::decimal as home_expected_goals,
    (fixture_data->'xG'->>'a')::decimal as away_expected_goals

from source_data