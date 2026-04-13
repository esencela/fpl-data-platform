# 002 - Missing historic team data strategy

## Context
Historic FPL data source does not contain team data for 2016/17 - 2018/19 seasons.

## Decision
A csv file containing historic team identifiers and names has been manually created by inferring from player data. This has been added to seeds/ in dbt.

## Notes
- FPL team data contains team strength fields which cannot be inferred
- Manually filling data might produce typos and inconsistencies in downstream modelling

## Considerations
- Add tests to ensure relationships between ids and matching names
- Team strength values can be modelled using available team-season data