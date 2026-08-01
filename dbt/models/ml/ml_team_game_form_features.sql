{{ config(
    materialized='table',
    alias='team_game_form_features'
)}}

{% set stat_columns = [
    'goals_scored',
    'goals_conceded',
    'shots',
    'shots_against',
    'expected_goals',
    'expected_goals_conceded',
    'xg_diff',
    'xgc_diff',
    'penalties_scored',
    'penalties_taken',
    'penalties_conceded',
    'passes',
    'deep_completions',
    'passes_against',
    'deep_completions_against',
    'defensive_actions',
    'passes_per_defensive_action',
    'influence',
    'creativity',
    'threat',
    'ict_index',
    'influence_against',
    'creativity_against',
    'threat_against',
    'ict_index_against'
] %}

with team_features as (
    select
        tg.fixture_key,
        team_id,
        at_home,
        count(*) over last_5_games as games_played_prior,

        {% for stat in stat_columns %}
        avg({{ stat }}) over last_5_games as team_{{ stat }}_per_game_last_5{{ "," if not loop.last }}
        {% endfor %}

    from {{ ref('fact_team_game') }} tg
    join {{ ref('dim_fixture') }} f
        on tg.fixture_key = f.fixture_key
    window last_5_games as (
        partition by team_id, season
        order by kickoff_time
        rows between 5 preceding and 1 preceding
    )
)

select 
    us.*,

    opp.games_played_prior as opp_games_played_prior,

    {% for stat in stat_columns %}
    opp.team_{{ stat }}_per_game_last_5 as opp_team_{{ stat }}_per_game_last_5{{ "," if not loop.last }}
    {% endfor %}

from team_features us
join team_features opp
    on us.fixture_key = opp.fixture_key
    and us.team_id != opp.team_id