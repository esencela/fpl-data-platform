# 001 - FPL historic data sourcing strategy

## Context
FPL API data is limited to current season data which is insufficient for this project. The platform requires multi-season data for historical analysis and training predictive models.

## Decision
A historic data source is available on GitHub at https://github.com/vaastav/Fantasy-Premier-League. This repo contains data from historic seasons previously extracted from the FPL API and largely shares the same schema. This will be used as a complementary data source to enhance the platform. This data will only be used from before FPL API data was initially extracted as a one-time historic data fill.

## Notes
- Schema is inconsistent over seasons, especially in earlier years
- Data has only been collected since the 2016/17 PL season, ideally more data would be available
- Certain data is completely missing for early seasons - fixture data unavailable before 2018/19 season, team data unavailable before 19/20 seasons, defensive and expected stats unavailable for certain seasons
- Gameweek data from 2019/20 season is affected by pandemic and lockdown - Gameweek numbers are as high as 47

## Considerations
- Alternate sources can be found for missing defensive and expected stats
- Missing team and fixture data can be inferred from available game and player data