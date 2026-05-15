{{ config(materialized='table') }}

with home_games as (
    select
        fixture_key,
        team_id as home_team_id,
        sum(goals) as home_team_score,
        sum(expected_goals) as home_expected_goals,
        sum(yellow_cards) as home_yellow_cards,
        sum(red_cards) as home_red_cards,
        sum(influence) as home_influence,
        sum(creativity) as home_creativity,
        sum(threat) as home_threat,
        sum(ict_index) as home_ict_index

    from 
        {{ ref('fact_player_game') }}    
    where
        at_home = true
    group by 
        fixture_key,
        team_id
),

away_games as (
    select
        fixture_key,
        team_id as away_team_id,
        sum(goals) as away_team_score,
        sum(expected_goals) as away_expected_goals,
        sum(yellow_cards) as away_yellow_cards,
        sum(red_cards) as away_red_cards,
        sum(influence) as away_influence,
        sum(creativity) as away_creativity,
        sum(threat) as away_threat,
        sum(ict_index) as away_ict_index

    from 
        {{ ref('fact_player_game') }}    
    where
        at_home = false
    group by 
        fixture_key,
        team_id
)

select
    home.fixture_key,

    -- Team identifiers
    home.home_team_id,
    away.away_team_id,

    -- Goal stats
    home.home_team_score,
    away.away_team_score,
    home.home_expected_goals,
    away.away_expected_goals,
    home.home_team_score - home.home_expected_goals as home_xg_diff,
    away.away_team_score - away.away_expected_goals as away_xg_diff,

    -- FPL metrics
    home.home_influence,
    home.home_creativity,
    home.home_threat,
    home.home_ict_index,
    away.away_influence,
    away.away_creativity,
    away.away_threat,
    away.away_ict_index,
    
    -- Discipline
    home.home_yellow_cards,
    home.home_red_cards,
    away.away_yellow_cards,
    away.away_red_cards

from home_games home
join away_games away
    on home.fixture_key = away.fixture_key