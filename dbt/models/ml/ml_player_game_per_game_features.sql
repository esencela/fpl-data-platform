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
    spine.player_game_key,
    spine.fixture_key,
    spine.season,
    spine.player_id,
    spine.team_id,
    spine.at_home,

    sum(case when played then 1 else 0 end) over w as games_played_prior,
    sum(shots) over w as shots_taken_prior,
    count(*) over w as games_prior,
    sum(case when played then 1 else 0 end) over w / nullif(count(*) over w, 0)::numeric as appearance_rate,
    sum(case when started then 1 else 0 end) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as starting_rate,
    sum(case when clean_sheet then 1 else 0 end) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as clean_sheet_rate,
    sum(goals) over w / nullif(sum(shots) over w, 0)::numeric as shot_conversion_rate,

    {% for stat in stat_columns %}
    sum({{ stat }}) over w / nullif(sum(case when played then 1 else 0 end) over w, 0)::numeric as {{ stat }}_per_game{{ "," if not loop.last }}
    {% endfor %}


from {{ ref('ml_player_fixture_spine') }} spine
left join {{ ref('fact_player_game') }} pg
    on spine.player_game_key = pg.player_game_key
window w as (
    partition by spine.player_id, spine.season
    order by spine.kickoff_time
    rows between unbounded preceding and 1 preceding
)