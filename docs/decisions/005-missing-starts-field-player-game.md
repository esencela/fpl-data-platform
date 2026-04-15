# 005 - Missing starts field in player-game data strategy

## Context
Vaastav repo data does not contain 'starts' column from 22/23 season and earlier. This column is necessary for downstream machine learning to predict fpl points per game and start chance.

## Decision
We can naively impute 'starts' data by selecting the 11 players with the most minutes for each team in each game. A new field will be added to flag rows that have imputed 'starts' value in the int_player_game model.

## Notes
- This method will misclassify some data - e.g. a player who starts gets injured in the first half. When used on data with available starts field, 1.3% were incorrect

## Considerations
- Including missing field flag in downstream machine learning can be tested for improving performance