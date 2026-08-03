{{ config(
    materialized='table',
    alias='player_game_form_features'
) }}

{% set stat_columns = [
    'goals',
    'assists',
    'goal_involvements',
    'shots',
    'key_passes',
    'goals_conceded',
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
    player_game_key,
    pg.fixture_key,
    f.season,
    player_id,
    team_id,

    count(*) over last_30_days as games_last_30_days,
    sum(minutes) over last_30_days as minutes_last_30_days,
    sum(minutes) over last_30_days / nullif(count(*) over last_30_days, 0)::numeric as avg_minutes_last_30_days,

    {% for stat in stat_columns %}
    sum({{ stat }}) over last_30_days as {{ stat }}_last_30_days,
    sum({{ stat }}) over last_30_days / nullif(sum(minutes) over last_30_days, 0)::numeric * 90 as {{ stat }}_per_90_last_30_days{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('fact_player_game') }} pg
join {{ ref('dim_fixture') }} f
    on pg.fixture_key = f.fixture_key
window last_30_days as (
    partition by player_id
    order by date_key
    range between interval '30 days' preceding and current row
    exclude current row
)