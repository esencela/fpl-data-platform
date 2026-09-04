{{ config(
    alias='season_features',
    materialized='table'
)}}

{% set stat_columns = [
    'bps'
] %}

with kickoff_agg as (
    select
        season,
        kickoff_time,
        count(*) as n_games,

        {% for stat in stat_columns %}
        sum({{ stat }}) as cum_{{ stat }}{{ "," if not loop.last}}
        {% endfor %}

    from {{ ref('fact_player_game') }} pg
    join {{ ref('dim_fixture') }} f
        on pg.fixture_key = f.fixture_key
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
    pg.player_game_key,
    pg.fixture_key,
    f.season,
    f.kickoff_time,
    coalesce(kc.cum_n_games, 0) as games_this_season,

    {% for stat in stat_columns %}
    kc.cum_{{ stat }} / nullif(kc.cum_n_games, 0) as avg_{{ stat }}_this_season{{ "," if not loop.last}}
    {% endfor %}

from {{ ref('fact_player_game') }} pg
join {{ ref('dim_fixture') }} f
    on pg.fixture_key = f.fixture_key
join kickoff_cumulative kc
    on f.season = kc.season
    and f.kickoff_time = kc.kickoff_time