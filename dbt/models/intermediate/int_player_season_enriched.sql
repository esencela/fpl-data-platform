{{ config(
    alias='player_season_enriched',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_season_key']
)}}

-- Fix inconsistent fpl ids with map
with id_map as (
    select
        *
    from {{ ref('int_player_season_base') }} base
    left join {{ ref('fpl_player_id_map') }} map
        on base.fpl_player_id = map.from_player_id
),

id_fixed as (
    select
        *,
        coalesce(to_player_id, fpl_player_id) as canon_fpl_player_id
    from id_map
),

-- Join understat ids
understat_joined as (
    select
        s.*,
        map.understat_id as understat_player_id
    from id_fixed s
    left join {{ ref('int_player_id_map') }} map
        on s.canon_fpl_player_id = map.fpl_player_id
)

select
    -- Identifiers
    player_season_key,    
    season,
    canon_fpl_player_id as fpl_player_id,
    understat_player_id,
    fpl_player_season_id,
    fpl_team_id,

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

from understat_joined