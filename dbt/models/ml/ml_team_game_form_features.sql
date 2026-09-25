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

with played_form as (
    select
        spine.fixture_key,
        spine.season,
        spine.team_id,
        spine.at_home,
        spine.kickoff_time,

        count(*) over last_5_games as games_played_prior,

        {% for stat in stat_columns %}
        avg({{ stat }}) over last_5_games as team_{{ stat }}_per_game_last_5{{ "," if not loop.last }}
        {% endfor %}

    from {{ ref('ml_team_fixture_spine') }} spine
    left join {{ ref('fact_team_game') }} tg
        on spine.fixture_key = tg.fixture_key
        and spine.team_id = tg.team_id
    where spine.finished
    window last_5_games as (
        partition by spine.team_id, spine.season
        order by spine.kickoff_time
        rows between 5 preceding and 1 preceding
    )
),

current_form as (
    select distinct on (team_id, season)
        fixture_key,
        season,
        team_id,
        at_home,

        games_played_prior,

        {% for stat in stat_columns %}
        team_{{ stat }}_per_game_last_5{{ "," if not loop.last }}
        {% endfor %}

    from played_form
    order by team_id, season, kickoff_time desc
),

team_features as (
    select
        spine.fixture_key,
        spine.team_id,
        spine.at_home,
        spine.finished,
        coalesce(played.games_played_prior, current.games_played_prior) as games_played_prior,

        {% for stat in stat_columns %}
        coalesce(played.team_{{ stat }}_per_game_last_5, current.team_{{ stat }}_per_game_last_5) as team_{{ stat }}_per_game_last_5{{ "," if not loop.last }}
        {% endfor %}

    from {{ ref('ml_team_fixture_spine') }} spine
    left join played_form played
        on spine.fixture_key = played.fixture_key
        and spine.team_id = played.team_id
    left join current_form current
        on spine.season = current.season
        and spine.team_id = current.team_id
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