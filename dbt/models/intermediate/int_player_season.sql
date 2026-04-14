{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_season_pk']
) }}

with combined as (
    select 
        *,
        'fpl' as source
        
    from {{ ref('stg_fpl__player_season') }}
    union all
    (select 
        *,
        'vaastav' as source

    from {{ ref('stg_vaastav__player_season') }})
),

sourced as (
    select
        *,
        row_number() over (
            partition by season, player_season_id
            order by case
                when source = 'fpl' then 1
                else 2
            end
        ) as r
    from combined
)

select
    -- Identifiers
    concat(season, '_', player_season_id) as player_season_pk,    
    season,
    player_id,
    player_season_id,
    team_id,

    -- Personal info
    first_name,
    second_name,
    known_name,
    web_name,
    country_id,
    birth_date,

    -- FPL info
    position,
    now_cost

from sourced
where r = 1