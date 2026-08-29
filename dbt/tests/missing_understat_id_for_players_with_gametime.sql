-- Understat player IDs are missing for some players in the int_player_game_enriched table. 
-- This test checks for players with gametime in int_player_game_base (minutes > 0) but no understat_player_id.
with total_minutes_for_null_understat_id as (
    select
        fpl_player_id,
        sum(fpl_minutes) as total_minutes
    from {{ ref('int_player_game_enriched')}}
    where understat_player_id is null
    group by fpl_player_id
)

select *
from total_minutes_for_null_understat_id
where total_minutes > 0