{{ config(
    materialized='table',
    alias='player_fixture_spine'
) }}

with played as (
	select
		pg.player_game_key,
        f.season,
        pg.fixture_key,
        pg.player_id,
        pg.team_id,
        pg.at_home,
        f.kickoff_time,
        f.finished
    from {{ ref('fact_player_game') }} pg
    join {{ ref('dim_fixture') }} f 
		on pg.fixture_key = f.fixture_key
),

upcoming as (
	select 
		null::text as player_game_key,
        f.season,
		f.fixture_key,
		ps.player_id,
		ps.team_id,
		(team_id = home_team_id) as at_home,
		f.kickoff_time,
		f.finished	
	from {{ ref('fact_player_season') }} ps
	join {{ ref('dim_fixture') }} f
		on ps.team_id in (f.home_team_id, f.away_team_id)
		and ps.season = f.season
	where f.finished = false
)

select *
from played
union all
select *
from upcoming