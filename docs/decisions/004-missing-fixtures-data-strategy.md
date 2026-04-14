# 004 - Missing historic fixture data strategy

## Context
Data pulled from the vaastav repo does not contain fixture data for the 16/17 and 17/18 seasons. This data is necessary for season and team aggregations in downstream analytics/ml.

## Decision
Data can be inferred from historic player-game data extracted from the vaastav repo. A separate staging model has been created to handle this. This data will be merged with fpl and vaastav fixture data in the intermediate fixtures model.

## Notes
- Fixture difficulty cannot be inferred from available data
- Unique fixture ids are not available in player-game data

## Considerations
- Fixture difficulty can be modelled with machine learning using available team and player data
- A composite key will be created to uniquely identify fixtures (season + '_' + fixture_season_id)