{{ config(
    alias='league_season_features',
    materialized='table'
)}}

{% set stat_columns = [
    'bps'
] %}

with kickoff_agg as (
    select
        spine.season,
        spine.kickoff_time,
        sum(case when spine.finished then 1 else 0 end) as n_games,

        {% for stat in stat_columns %}
        sum({{ stat }}) as cum_{{ stat }}{{ "," if not loop.last}}
        {% endfor %}

    from {{ ref('ml_player_fixture_spine') }} spine
    left join {{ ref('fact_player_game') }} pg
        on spine.player_game_key = pg.player_game_key
    group by season, kickoff_time
),

kickoff_cumulative as (
    select
        season,
        kickoff_time,
        sum(n_games) over w as cum_n_games,

        {% for stat in stat_columns %}
        sum(cum_{{ stat }}) over w as cum_{{ stat }}{{ "," if not loop.last}}
        {% endfor %}

    from kickoff_agg
    window w as (
        partition by season
        order by kickoff_time
        rows between unbounded preceding and 1 preceding
    )
)

select
    f.fixture_key,
    f.season,
    f.kickoff_time,
    f.finished,
    coalesce(kc.cum_n_games, 0) as games_this_season,

    {% for stat in stat_columns %}
    kc.cum_{{ stat }} / nullif(kc.cum_n_games, 0) as avg_{{ stat }}_this_season{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('dim_fixture') }} f
join kickoff_cumulative kc
    on f.season = kc.season
    and f.kickoff_time = kc.kickoff_time