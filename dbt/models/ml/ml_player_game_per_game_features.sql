{{ config(
    alias='player_game_per_game_features',
    materialized='table'
) }}

{% set stat_columns = [
    'minutes',
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
    player_game_key,
    pg.fixture_key,
    season,
    player_id,

    sum(case when played then 1 else 0 end) over w as games_played_prior,
    sum(case when started then 1 else 0 end) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as starting_rate,
    sum(case when clean_sheet then 1 else 0 end) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as clean_sheet_rate,

    {% for stat in stat_columns %}
    sum({{ stat }}) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as {{ stat }}_per_game{{ "," if not loop.last }}
    {% endfor %}


from {{ ref('fact_player_game') }} pg
join {{ ref('dim_fixture') }} f
on pg.fixture_key = f.fixture_key
window w as (
    partition by player_id, season
    order by date_key
    rows between unbounded preceding and 1 preceding
)