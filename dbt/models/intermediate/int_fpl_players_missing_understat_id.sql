{{ config(
    alias='fpl_players_missing_understat_id',
    materialized='table'
)}}

-- Understat players will have null player id if they have no game time
-- Find players who have game time and are still missing an understat player id
with total_minutes_for_null_understat_id as (
    select
        fpl_player_id,
        sum(fpl_minutes) as total_minutes
    from {{ ref('int_player_game_enriched')}}
    where understat_player_id is null
    group by fpl_player_id
),

missing_ids as (
    select 
        fpl_player_id
    from total_minutes_for_null_understat_id
    where total_minutes > 0
),

-- Get FPL player info from most recent season
season_ranked as (
    select
        fpl_player_id,
        understat_player_id,
        first_name,
        second_name,
        web_name,
        row_number() over (
            partition by fpl_player_id
            order by season desc
        ) as rn
    from {{ ref('int_player_season_enriched')}}
),

fpl_missing_info as (
    select
        fpl_player_id,
        understat_player_id,
        first_name,
        second_name,
        web_name
    from season_ranked
    where rn = 1
        and fpl_player_id in (
            select
                fpl_player_id
            from missing_ids
        )
)

select
	m.fpl_player_id,
	m.first_name,
	m.second_name,
	m.web_name,
	e.understat_player_id,
    case 
        when b.at_home then f.home_understat_team_id
        else f.away_understat_team_id
    end as understat_team_id,
    e.understat_fixture_id,
	b.*
from fpl_missing_info m
join {{ ref('int_player_game_enriched') }} e
	on m.fpl_player_id = e.fpl_player_id
left join {{ ref('int_player_game_base') }} b
	on e.player_game_key = b.player_game_key
left join {{ ref('int_fixtures') }} f
    on b.fixture_key = f.fixture_key