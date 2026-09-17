{{ config(
    alias='player_game_per_90_features',
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
    spine.player_game_key,
    spine.fixture_key,
    spine.season,
    spine.player_id,
    spine.team_id,
    sum(minutes) over w as total_minutes_prior,

    {% for stat in stat_columns %}
    sum({{ stat }}) over w / nullif(sum(minutes) over w, 0)::numeric * 90 as {{stat}}_per_90{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('ml_player_fixture_spine') }} spine
left join {{ ref('fact_player_game') }} pg
on spine.player_game_key = pg.player_game_key
window w as (
    partition by spine.player_id, spine.season
    order by spine.kickoff_time
    rows between unbounded preceding and 1 preceding
)