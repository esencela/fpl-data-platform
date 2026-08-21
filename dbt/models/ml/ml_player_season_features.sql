{{ config(
    materialized='table',
    alias='player_season_features'
) }}

{% set stat_columns = [
    'goals', 
    'assists', 
    'goal_involvements', 
    'shots', 
    'key_passes', 
    'goals_conceded', 
    'own_goals', 
    'yellow_cards', 
    'red_cards', 
    'defensive_contributions', 
    'saves', 
    'bonus',
    'bps', 
    'influence', 
    'creativity',
    'threat',
    'ict_index', 
    'expected_goals', 
    'expected_assists', 
    'expected_goal_involvements', 
    'expected_goal_chain', 
    'expected_goal_buildup'
] %}

select
    player_season_key,
    player_id,
    season,
    games_total,
    games_played,
    games_started,
    total_minutes,
    shots,
    fpl_position,

    games_played / nullif(games_total, 0)::numeric as appearance_rate,
    games_started / nullif(games_played, 0)::numeric as starting_rate,
    clean_sheets / nullif(games_played, 0)::numeric as clean_sheet_rate,
    goals / nullif(shots, 0)::numeric as shot_conversion_rate,
    total_minutes / nullif(games_played, 0)::numeric as minutes_per_game,

    {% for stat in stat_columns %}
    {{ stat }} / nullif(games_played, 0)::numeric as {{ stat }}_per_game,
    {% endfor %}

    {% for stat in stat_columns %}
    {{ stat }} / nullif(total_minutes, 0)::numeric * 90 as {{ stat }}_per_90{{ "," if not loop.last }}
    {% endfor %}

from {{ ref('fact_player_season') }} ps