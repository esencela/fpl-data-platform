{{ config(materialized='table') }}

select
	fixture.fixture_key,
	fixture.season,
	fixture.fpl_fixture_season_id,
	fixture.gameweek_id,
	fixture.gameweek as canon_gameweek,
	fixture.kickoff_time,
	fixture.finished,
	home.team_id as home_team_id,
	away.team_id as away_team_id
from {{ ref('int_fixtures') }} as fixture
join {{ ref('int_team_season') }} as home
	on fixture.home_team_season_key = home.team_season_key
join {{ ref('int_team_season') }} as away
	on fixture.away_team_season_key = away.team_season_key