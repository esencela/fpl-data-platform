{{ config(
    alias='understat_teams',
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
        key as team_id,
        value as team_data
    from latest_snapshot,
    jsonb_each(raw_data->'teams')
),

-- Team endpoint data is missing three letter team codes, so we need to get this from the fixture data
fixture_data as (
    select
        season,
        jsonb_array_elements(raw_data->'dates') as fixture_data
    from latest_snapshot
),

fixture_team_data as (
    select
        distinct (fixture_data->'h'->>'id')::int as team_id,
        (fixture_data->'h'->>'short_title') as short_name
    from fixture_data
),

team_data as (
    select
        distinct team_id::int as team_id,
        (team_data->>'title') as team_name
    from source_data
)

select
    t.team_id,
    t.team_name,
    f.short_name
from team_data t
left join fixture_team_data f
    on t.team_id = f.team_id