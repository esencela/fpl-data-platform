{{ config(
    materialized='incremental',
    alias='shots',
    incremental_strategy='delete_insert',
    unique_key='shot_id'
)}}

with fixture_data_added as (
    select
        shot.*,
        fixture.fixture_key,
        case
            when shot.is_home then fixture.home_team_season_key
            else fixture.away_team_season_key
        end as team_season_key

    from {{ ref('stg_understat__shots') }} shot
    left join {{ ref('int_fixtures') }} fixture
        on shot.match_id = fixture.understat_fixture_id
),

team_id_added as (
    select
        shot.*,
        team.team_id as fpl_team_id
    from fixture_data_added shot
    left join {{ ref('int_team_season') }} team
        on shot.team_season_key = team.team_season_key
),

player_id_added as (
    select 
        shot.*,
        map.fpl_player_id
    from team_id_added shot
    left join {{ ref('int_player_id_map')}} map
        on shot.player_id = map.understat_id
)

select
    -- Identifiers
    shot_id,
    season,
    fixture_key,
    fpl_player_id,
    fpl_team_id,

    -- Context
    player_name,
    player_assisted,
    team_name,
    is_home,

    -- Shot info
    minute,
    situation,
    shot_type,
    outcome,
    last_action,

    -- Shot data
    expected_goals,
    x,
    y

from player_id_added