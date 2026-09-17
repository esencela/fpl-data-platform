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

-- Calculate form for player over 30 days before fixture, used for past games.
with played_form as (
    select
        spine.player_game_key,
        spine.season,
        spine.fixture_key,
        spine.player_id,
        spine.team_id,
        spine.kickoff_time,

        count(*) over last_30_days as games_last_30_days,
        coalesce(sum(minutes) over last_30_days, 0) as minutes_last_30_days,
        sum(minutes) over last_30_days / nullif(count(*) over last_30_days, 0)::numeric as avg_minutes_last_30_days,

        {% for stat in stat_columns %}
        sum({{ stat }}) over last_30_days as {{ stat }}_last_30_days,
        sum({{ stat }}) over last_30_days / nullif(sum(minutes) over last_30_days, 0)::numeric * 90 as {{ stat }}_per_90_last_30_days{{ "," if not loop.last}}
        {% endfor %}

    from {{ ref('ml_player_fixture_spine') }} spine
    left join {{ ref('fact_player_game') }} pg
        on spine.player_game_key = pg.player_game_key
    where spine.finished
    window last_30_days as (
        partition by spine.player_id
        order by spine.kickoff_time
        range between interval '30 days' preceding and current row
        exclude current row
    )
),

-- Capture most recent form for each player, used for upcoming games.
current_form as (
    select distinct on (player_id)
        player_game_key,
        season,
        fixture_key,
        player_id,
        team_id,

        games_last_30_days,
        minutes_last_30_days,
        avg_minutes_last_30_days,

        {% for stat in stat_columns %}
        {{ stat }}_last_30_days,
        {{ stat }}_per_90_last_30_days{{ "," if not loop.last}}
        {% endfor %}

    from played_form
    order by player_id, kickoff_time desc
)

select 
    spine.player_game_key,
    spine.season,
    spine.fixture_key,
    spine.player_id,
    spine.team_id,

    coalesce(played.games_last_30_days, current.games_last_30_days) as games_last_30_days,
    coalesce(played.minutes_last_30_days, current.minutes_last_30_days) as minutes_last_30_days,
    coalesce(played.avg_minutes_last_30_days, current.avg_minutes_last_30_days) as avg_minutes_last_30_days,

    {% for stat in stat_columns %}
    coalesce(played.{{ stat }}_last_30_days, current.{{ stat }}_last_30_days) as {{ stat }}_last_30_days,
    coalesce(played.{{ stat }}_per_90_last_30_days, current.{{ stat }}_per_90_last_30_days) as {{ stat }}_per_90_last_30_days{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('ml_player_fixture_spine') }} spine
left join played_form played
    on spine.player_game_key = played.player_game_key
left join current_form current
    on spine.player_id = current.player_id