{{ config(materialized='table') }}

select
	-- Identifiers
	fixture.fixture_key,
	fixture.fpl_fixture_id,
	fixture.fpl_fixture_season_id,
	fixture.understat_fixture_id,

	-- Fixture info
	fixture.season,
	fixture.gameweek_id,
	fixture.gameweek as canon_gameweek,
	fixture.kickoff_time,
	fixture.finished,

	-- Team identifiers
	home.team_id as home_team_id,
	away.team_id as away_team_id
	
from {{ ref('int_fixtures') }} as fixture
join {{ ref('int_team_season') }} as home
	on fixture.home_team_season_key = home.team_season_key
join {{ ref('int_team_season') }} as away
	on fixture.away_team_season_key = away.team_season_key