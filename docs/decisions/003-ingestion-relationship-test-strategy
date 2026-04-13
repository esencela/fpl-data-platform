# 003 - ID relationship testing strategy for ingested data

## Context
FPL API data uses seperate unique identifiers for players, teams, fixtures and season identifiers (1 - n where n is the amount of players, teams, fixtures etc.). These season identifiers are used in the api data to reference other tables and are not globally unique. This makes relationship testing impossible on raw data.

## Decision
Relationship testing will be implemented in intermediate models rather than staging. Surrogate keys will be created in intermediate tables to uniquely identify elements. 

Staging models will only use basic testing and sanity checks for raw data.

## Notes
- This decision ensures staging models reflect raw data
- Intermediate becomes the initial trusted relational layer