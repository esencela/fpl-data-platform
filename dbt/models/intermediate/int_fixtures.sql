{{ config(
    alias='fixtures',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['fixture_key']
)}}

with combined as (
    select
        *,
        'fpl' as source
    from {{ ref('stg_fpl__fixtures') }}
    union all
    select
        *,
        'vaastav' as source
    from {{ ref('stg_vaastav__fixtures') }}
    union all
    select
        *,
        'inferred' as source
    from {{ ref('stg_vaastav__inferred_fixtures') }}
),

-- If two rows clash, prioritise by source
prioritised as (
    select
        *,
        row_number() over (
            partition by season, fixture_season_id
            order by case
                when source = 'fpl' then 1
                when source = 'vaastav' then 2
                else 3
            end
        ) as r
    from combined
),

-- Gameweek numbers are disrupted in 2020 season due to pandemic - gw 30-38 becomes 39-47
gameweeks_corrected as (
    select
        *,
        case 
            when season = 2020 and gameweek_id > 38 then gameweek_id - 9
            else gameweek_id
        end as corrected_gameweek
)

select
    -- Identifiers
    concat(season, '_', fixture_season_id) as fixture_key,
    season,
    fixture_id as fpl_fixture_id,
    fixture_season_id as fpl_fixture_season_id,

    -- Fixture info
    gameweek_id,
    corrected_gameweek as gameweek,
    kickoff_time,
    finished,

    -- Team info
    concat(season, '_', home_team_season_id) as home_team_season_key,
    home_team_season_id as home_fpl_team_season_id,
    concat(season, '_', away_team_season_id) as away_team_season_key,
    away_team_season_id as away_fpl_team_season_id,
    home_team_score,
    away_team_score,
    home_team_difficulty,
    away_team_difficulty

from prioritised
where r = 1