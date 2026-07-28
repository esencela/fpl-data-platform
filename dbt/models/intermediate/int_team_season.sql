{{ config(
    alias='team_season',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['team_season_key'],
    on_schema_change='append_new_columns'
) }}

with combined as (
    select 
        *,
        'fpl' as source
    from {{ ref('stg_fpl__teams') }}
    union all
    select
        *,
        'vaastav' as source
    from {{ ref('stg_vaastav__teams') }}
    union all
    select
        *,
        'inferred' as source
    from {{ ref('missing_teams') }}
),

-- If rows clash, prioritise by source
prioritised as (
    select
        *,
        row_number() over(
            partition by season, team_season_id
            order by case
                when source = 'fpl' then 1
                when source = 'vaastav' then 2
                else 3
            end
        ) as r
    from combined
),

understat_ids_added as (
    select
        p.*,
        map.understat_team_id
    from prioritised p
    join {{ ref('team_id_map') }} map
        on p.team_id = map.fpl_team_id
    where r = 1
)

select 
    -- Team identifiers
    concat(season, '_', team_season_id) as team_season_key,
    season,
    team_id,
    understat_team_id,
    team_season_id,

    -- Team names
    name as team_name,
    short_name,

    -- Team strength metrics
    strength_overall_home,
    strength_overall_away,
    strength_attack_home,
    strength_attack_away,
    strength_defence_home,
    strength_defence_away

from understat_ids_added