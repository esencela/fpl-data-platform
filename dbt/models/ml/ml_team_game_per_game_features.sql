{{ config(
    alias='team_game_per_game_features',
    materialized='table'
) }}

{% set stat_columns = [
    'goals_scored',
    'goals_conceded',
    'shots',
    'shots_against',
    'expected_goals',
    'expected_goals_conceded',
    'xg_diff',
    'xgc_diff',
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
    'ict_index_against',
    'yellow_cards',
    'red_cards'
] %}

with team_features as (
    select
        tg.fixture_key,
        team_id,
        at_home,
        
        count(*) over w as games_played_prior,

        extract(
            day from (f.kickoff_time - lag(f.kickoff_time) over w_all)
        ) as team_days_since_last_game,

        {% for stat in stat_columns %}
        avg({{ stat }}) over w as team_{{ stat }}_per_game{{ "," if not loop.last }}
        {% endfor %}

    from {{ ref('fact_team_game') }} tg
    join {{ ref('dim_fixture') }} f
    on tg.fixture_key = f.fixture_key
    window 
        w as (
            partition by team_id, season
            order by kickoff_time
            rows between unbounded preceding and 1 preceding
        ),
        w_all as (
            partition by team_id, season
            order by kickoff_time
        )

)

select
    us.*,

    opp.games_played_prior as opp_games_played_prior,
    opp.team_days_since_last_game as opp_team_days_since_last_game,

    {% for stat in stat_columns %}
    opp.team_{{ stat }}_per_game as opp_team_{{ stat }}_per_game{{ "," if not loop.last }}
    {% endfor %}

from team_features us
join team_features opp
    on us.fixture_key = opp.fixture_key
    and us.team_id <> opp.team_id