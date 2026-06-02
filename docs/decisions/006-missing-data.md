# 006 - Missing Data

## Context
FPL API data is missing a lot of fields that is vital for the platform and machine learning - Shots, xg, xa, starts, key passes (Some only for certain seasons)

## Decision
A new free data source has been selected for these missing fields - Understat contains advanced shot and expected data. This can be merged into our data models with a id mapping dataset publically available on GitHub.

## Notes
- This solution will override decision 005 for missing starts data
- Separate raw and serving tables will be created for understat specific data and merged into intermediate models

## Considerations
- Some player ids are missing from the id map. Tests will be implemented to identify players with missing ids.
- Understat id is not available for players who have zero minutes overall