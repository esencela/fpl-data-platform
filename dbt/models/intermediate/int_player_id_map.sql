{{ config(
    materialized='table',
    alias='player_id_map'
) }}

-- Raw id mapping duplicates understat id across correct player and players who have similar names with no minutes
with duplicates as (
    select
        understat_id
    from {{ ref('stg_player_id_map') }}
    where understat_id is not null
    group by understat_id
    having count(*) > 1
),

player_ids as (
    select
        fpl_player_id,
        understat_id
    from {{ ref('stg_player_id_map') }}
    where understat_id in (select understat_id from duplicates)
),

total_minutes as (
    select
        ps.fpl_player_id,
        sum(pg.minutes) as sum_minutes
    from {{ ref('int_player_game') }} pg
    join {{ ref('int_player_season')}} ps
        on pg.player_season_key = ps.player_season_key
    where ps.fpl_player_id in (select fpl_player_id from player_ids)
    group by ps.fpl_player_id
),

-- Remove understat_id for players with no minutes played
removed_duplicates as (
    select 
        fpl_player_id,
        case
            when sum_minutes = 0 then null
            else understat_id
        end as understat_id,
        1 as cleaned
    from player_ids
    join total_minutes using (fpl_player_id)
),

cleaned_understat as (
    select 
        fpl_player_id,
        case 
            when cleaned = 1 then clean.understat_id
            else raw.understat_id
        end as understat_id
    from {{ ref('stg_player_id_map') }} as raw
    left join removed_duplicates as clean
        using (fpl_player_id)
),

-- Map inconsistent fpl ids
fpl_id_mapped as (
    select
        coalesce(map.to_player_id, clean.fpl_player_id) as fpl_player_id,
        understat_id
    from cleaned_understat clean
    left join {{ ref('fpl_player_id_map') }} map
        on clean.fpl_player_id = map.from_player_id
)

select *
from fpl_id_mapped