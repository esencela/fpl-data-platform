{{ config(
    alias='player_season_base',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_season_key']
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

-- If two rows clash, prioritise fpl source
prioritised as (
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
),

-- Replace position numbers with strings
position_strings as (
    select 
        *,
        case
            when position = 1 then 'GKP'
            when position = 2 then 'DEF'
            when position = 3 then 'MID'
            when position = 4 then 'FWD'
        end as position_str
    from prioritised
)

select
    -- Identifiers
    concat(season, '_', player_season_id) as player_season_key,    
    season,
    player_id as fpl_player_id,
    player_season_id as fpl_player_season_id,
    team_id as fpl_team_id,

    -- Personal info
    first_name,
    second_name,
    case
        when known_name = '' then null
        else known_name
    end as known_name,
    web_name,
    country_id,
    birth_date,

    -- FPL info
    position_str as position,
    now_cost

from position_strings
where r = 1