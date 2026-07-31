{{ config(materialized='table') }}

with home_games as (
    select
        fixture_key,
        home_team_id as team_id,
        true as at_home,

        home_team_score as goals_scored,
        away_team_score as goals_conceded,
        home_shots as shots,
        away_shots as shots_against,

        home_expected_goals as expected_goals,
        away_expected_goals as expected_goals_conceded,
        home_xg_diff as xg_diff,
        away_xg_diff as xgc_diff,

        home_penalties_scored as penalties_scored,
        home_penalties_taken as penalties_taken,
        away_penalties_taken as penalties_conceded,

        home_passes as passes,
        home_deep_completions as deep_completions,
        away_passes as passes_against,
        away_deep_completions as deep_completions_against,

        home_defensive_actions as defensive_actions,
        home_ppda as passes_per_defensive_action,

        home_influence as influence,
        home_creativity as creativity,
        home_threat as threat,
        home_ict_index as ict_index,

        away_influence as influence_against,
        away_creativity as creativity_against,
        away_threat as threat_against,
        away_ict_index as ict_index_against,

        home_yellow_cards as yellow_cards,
        home_red_cards as red_cards

    from {{ ref('fact_match') }}
),

away_games as (
    select
        fixture_key,
        away_team_id as team_id,
        false as at_home,

        away_team_score as goals_scored,
        home_team_score as goals_conceded,
        away_shots as shots,
        home_shots as shots_against,

        away_expected_goals as expected_goals,
        home_expected_goals as expected_goals_conceded,
        away_xg_diff as xg_diff,
        home_xg_diff as xgc_diff,

        away_penalties_scored as penalties_scored,
        away_penalties_taken as penalties_taken,
        home_penalties_taken as penalties_conceded,

        away_passes as passes,
        away_deep_completions as deep_completions,
        home_passes as passes_against,
        home_deep_completions as deep_completions_against,

        away_defensive_actions as defensive_actions,
        away_ppda as passes_per_defensive_action,

        away_influence as influence,
        away_creativity as creativity,
        away_threat as threat,
        away_ict_index as ict_index,

        home_influence as influence_against,
        home_creativity as creativity_against,
        home_threat as threat_against,
        home_ict_index as ict_index_against,

        away_yellow_cards as yellow_cards,
        away_red_cards as red_cards

    from {{ ref('fact_match') }}
)

select
    *
from home_games
union all
select
    *
from away_games