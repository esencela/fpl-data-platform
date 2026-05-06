-- Create schema layers
CREATE SCHEMA IF NOT EXISTS raw;

-- Create raw tables for fpl api data
CREATE TABLE IF NOT EXISTS raw.fpl_bootstrap_static (
    season INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.fpl_element_summary (
    season INT NOT NULL,
    player_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, player_id)
);

CREATE TABLE IF NOT EXISTS raw.fpl_fixtures (
    season INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.fpl_events (
    season INT NOT NULL,
    gameweek_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, gameweek_id)
);

-- Create indexes for raw fpl api tables
CREATE INDEX IF NOT EXISTS idx_fpl_bootstrap_static_season 
ON raw.fpl_bootstrap_static(season);

CREATE INDEX IF NOT EXISTS idx_fpl_bootstrap_static_jsonb
ON raw.fpl_bootstrap_static USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_element_summary_season_player
ON raw.fpl_element_summary(season, player_id);

CREATE INDEX IF NOT EXISTS idx_fpl_element_summary_jsonb
ON raw.fpl_element_summary USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_fixtures_season
ON raw.fpl_fixtures(season);

CREATE INDEX IF NOT EXISTS idx_fpl_fixtures_jsonb
ON raw.fpl_fixtures USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_events_season_gameweek
ON raw.fpl_events(season, gameweek_id);

CREATE INDEX IF NOT EXISTS idx_fpl_events_jsonb
ON raw.fpl_events USING GIN(raw_data);


-- Create raw tables for vaastav parquet data
CREATE TABLE IF NOT EXISTS raw.vaastav_players (
    season INT NOT NULL,
    player_season_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, player_season_id, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.vaastav_gws (
    season INT NOT NULL,
    player_season_id INT NOT NULL,
    fixture_season_id INT NOT NULL,
    gameweek_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, player_season_id, fixture_season_id, gameweek_id, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.vaastav_fixtures(
    season INT NOT NULL,
    fixture_season_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fixture_season_id, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.vaastav_teams(
    season INT NOT NULL,
    team_season_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, team_season_id, fetched_at)
);

-- Create indexes for raw vaastav tables
CREATE INDEX IF NOT EXISTS idx_vaastav_players_season_player
ON raw.vaastav_players(season, player_season_id);

CREATE INDEX IF NOT EXISTS idx_vaastav_players_jsonb
ON raw.vaastav_players USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_vaastav_gws_season
ON raw.vaastav_gws(season, player_season_id, fixture_season_id, gameweek_id);

CREATE INDEX IF NOT EXISTS idx_vaastav_gws_jsonb
ON raw.vaastav_gws USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_vaastav_fixtures_season_fixture
ON raw.vaastav_fixtures(season, fixture_id);

CREATE INDEX IF NOT EXISTS idx_vaastav_fixtures_jsonb
ON raw.vaastav_fixtures USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_vaastav_teams_season_team
ON raw.vaastav_teams(season, team_season_id);

CREATE INDEX IF NOT EXISTS idx_vaastav_teams_jsonb
ON raw.vaastav_teams USING GIN(raw_data);

-- Create raw tables for understat data
CREATE TABLE IF NOT EXISTS raw.understat_season_data (
    season INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.understat_shot_data (
    match_id VARCHAR(20) NOT NULL,
    raw_data JSONB NOT NULL,
    PRIMARY KEY (match_id)
);

-- Create indexes for raw understat tables
CREATE INDEX IF NOT EXISTS idx_understat_season_data_season
ON raw.understat_season_data(season);

CREATE INDEX IF NOT EXISTS idx_understat_season_data_jsonb
ON raw.understat_season_data USING GIN(raw_data);

CREATE INDEX IF NOT EXISTS idx_understat_shot_data_match_id
ON raw.understat_shot_data(match_id);

CREATE INDEX IF NOT EXISTS idx_understat_shot_data_jsonb
ON raw.understat_shot_data USING GIN(raw_data);