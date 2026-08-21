-- Understat player IDs are missing for some players in the int_player_game_enriched table. 
-- This test checks for players with gametime in int_player_game_base (minutes > 0) but no understat_player_id.
with total_minutes_for_null_understat_id as (
    select
        b.fpl_player_season_id,
        b.season,
        sum(b.minutes) as total_minutes
    from {{ ref('int_player_game_base') }} b
    left join {{ ref('int_player_game_enriched')}} e
        on b.player_game_key = e.player_game_key
    where e.understat_player_id is null
    group by b.fpl_player_season_id, b.season
)

select *
from total_minutes_for_null_understat_id
where total_minutes > 0