-- Create schema layers
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS serving;

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

-- Create indexes for raw tables
CREATE INDEX IF NOT EXISTS idx_fpl_bootstrap_static_season 
ON raw.fpl_bootstrap_static(season);

CREATE INDEX IF NOT EXISTS idx_fpl_bootstrap_static_jsonb
ON raw.fpl_bootstrap_static USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_element_summary_season_player
ON raw.fpl_element_summary(season, player_id);

CREATE INDEX IF NOT EXISTS idx_fpl_element_summary_jsonb
ON raw.fpl_element_summary USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_fixtures_season
ON raw.fpl_fixtures(season);

CREATE INDEX IF NOT EXISTS idx_fpl_fixtures_jsonb
ON raw.fpl_fixtures USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_fpl_events_season_gameweek
ON raw.fpl_events(season, gameweek_id);

CREATE INDEX IF NOT EXISTS idx_fpl_events_jsonb
ON raw.fpl_events USING GIN (raw_data);


-- Create raw tables for vaastav parquet data
CREATE TABLE IF NOT EXISTS raw.vaastav_players (
    season INT NOT NULL,
    player_season_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, player_season_id, fetched_at)
);