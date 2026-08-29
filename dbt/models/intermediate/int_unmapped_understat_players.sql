{{ config(
    alias='unmapped_understat_players',
    materialized='table'
)}}

select
    *
from {{ ref('stg_understat__player_game')}}
where player_id not in (
	select
		understat_player_id
	from dev_intermediate.player_game_enriched
	where understat_player_id is not null
)