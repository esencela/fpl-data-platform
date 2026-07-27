{{ config(
    alias='player_game_per90_features'
    materialized='table'
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
    'bps', 
    'influence', 
    'creativity', 
    'ict_index', 
    'expected_goals', 
    'expected_assists', 
    'expected_goal_involvements', 
    'expected_goal_chain', 
    'expected_goal_buildup'
] %}

select
    player_game_key,

    {% for stat in stat_columns %}
    SUM({{ stat }}) over w / nullif(sum(minutes) over w, 0)::numeric * 90 as {{stat}}_per_90{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('fact_player_game') }} pg
join {{ ref('dim_fixture') }} f
on pg.fixture_key = f.fixture_key
window w as (
    partition by player_id, season
    order by date_key
    rows between unbounded preceding and 1 preceding
)