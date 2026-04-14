{{ config(materialized='view') }}

-- Only get data from latest fetch
with latest_snapshot as (
    select
        season,
        fixture_season_id,
        raw_data,
        fetched_at,
        gameweek_id
    from {{ source('raw', 'vaastav_gws') }}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'vaastav_gws') }})
        and season < 2019
),

base as (
    select  
        season::int as season,
        fixture_season_id::int as fixture_season_id,
        gameweek_id::int as gameweek_id,
        (raw_data->>'kickoff_time')::timestamptz as kickoff_time,
        (raw_data->>'was_home')::boolean as was_home,
        (raw_data->>'opponent_team') as opponent_team,
        ((raw_data->>'team_h_score')::numeric)::int as home_team_score,
        ((raw_data->>'team_a_score')::numeric)::int as away_team_score,
        (raw_data->>'team_h_difficulty')::int as home_team_difficulty,
        (raw_data->>'team_a_difficulty')::int as away_team_difficulty

from latest_snapshot
),

fixtures as (
    select
        -- Identifiers
        null as fixture_id,
        season,
        fixture_season_id,

        -- Fixture info
        gameweek_id,
        kickoff_time,
        true as finished,

        -- Team info
        max(case when not was_home then opponent_team end) as home_team_season_id,
        max(case when was_home then opponent_team end) as away_team_season_id,
        max(home_team_score) as home_team_score,
        max(away_team_score) as away_team_score,
        null as home_team_difficulty,
        null as away_team_difficulty
    
    from base
    group by 2,3,4,5
)

select * from fixtures