-- Create schema layers
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS serving;

-- Create raw tables
CREATE TABLE IF NOT EXISTS raw.bootstrap_static (
    season INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.element_summary (
    season INT NOT NULL,
    player_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, player_id)
);

CREATE TABLE IF NOT EXISTS raw.fixtures (
    season INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, fetched_at)
);

CREATE TABLE IF NOT EXISTS raw.events (
    season INT NOT NULL,
    gameweek_id INT NOT NULL,
    raw_data JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, gameweek_id)
);

-- Create indexes for raw tables
CREATE INDEX IF NOT EXISTS idx_bootstrap_static_season 
ON raw.bootstrap_static(season);

CREATE INDEX IF NOT EXISTS idx_bootstrap_static_jsonb
ON raw.bootstrap_static USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_element_summary_season_player
ON raw.element_summary(season, player_id);

CREATE INDEX IF NOT EXISTS idx_element_summary_jsonb
ON raw.element_summary USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_fixtures_season
ON raw.fixtures(season);

CREATE INDEX IF NOT EXISTS idx_fixtures_jsonb
ON raw.fixtures USING GIN (raw_data);

CREATE INDEX IF NOT EXISTS idx_events_season_gameweek
ON raw.events(season, gameweek_id);

CREATE INDEX IF NOT EXISTS idx_events_jsonb
ON raw.events USING GIN (raw_data);