{{ config(materialized='table') }}

select
    shot_id,
    fixture_key,
    fpl_player_id as player_id,
    fpl_team_id as team_id,
    is_home as at_home,

    minute,
    situation,
    shot_type,
    outcome,
    last_action,

    expected_goals,
    x,
    y
from {{ ref('int_shots') }}