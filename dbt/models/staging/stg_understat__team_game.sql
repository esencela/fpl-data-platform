{{ config(
    alias='understat_team_game',
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
        key as team_id,
        value as team_data
    from latest_snapshot,
    jsonb_each(raw_data->'teams')
),

history as (
    select
        season,
        team_id,
        jsonb_array_elements(team_data->'history') as match_data    
    from source_data
)

select
    -- Identifiers
    season::int as season,
    team_id::int as team_id,

    -- Match info
    (match_data->>'date')::timestamp as match_date,
    case
        when match_data->>'h_a' = 'h' then true
        when match_data->>'h_a' = 'a' then false
        else null
    end as at_home,
    (match_data->>'scored')::int as goals_scored,
    (match_data->>'missed')::int as goals_conceded,

    -- Expected stats
    (match_data->>'xG')::decimal as expected_goals,
    (match_data->>'xGA')::decimal as expected_goals_conceded,
    (match_data->>'npxG')::decimal as non_penalty_expected_goals,
    (match_data->>'npxGA')::decimal as non_penalty_expected_goals_conceded,

    -- Passing stats
    (match_data->'ppda'->>'att')::int / (match_data->'ppda'->>'def')::int as passes_per_defensive_action,
    (match_data->'ppda_allowed'->>'att')::int / (match_data->'ppda_allowed'->>'def')::int as opponent_passes_per_defensive_action,
    (match_data->>'deep')::int as deep_completions,
    (match_data->>'deep_allowed')::int as deep_completions_allowed
        
from history