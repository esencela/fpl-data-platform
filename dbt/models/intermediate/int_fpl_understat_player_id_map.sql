{{ config(
    alias='fpl_understat_player_id_map',
    materialized='table'
) }}

-- Understat id mappings that were missing in extracted github mapppings
with missing_mappings as (
    select  
        fpl_player_id,
        understat_player_id
    from {{ ref('int_fpl_understat_similarity_scores') }}
    -- Select the best id mapping over a certain similarity threshold, manually map any others
    where rank = 1 
        and similarity > 0.7
),

-- Join into extracted map
joined_mappings as (
    select
        coalesce(missing.fpl_player_id, map.fpl_player_id) as fpl_player_id,
        coalesce(missing.understat_player_id, map.understat_id) as understat_player_id
    from {{ ref('int_player_id_map') }} map
    full outer join missing_mappings missing
        on map.fpl_player_id = missing.fpl_player_id
)

select *
from joined_mappings