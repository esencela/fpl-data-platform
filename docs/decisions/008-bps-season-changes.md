# 008 - Bps season changes

## Context
FPL uses a bonus points system (bps) to award bonus points, the three highest scoring players in a game receive 3, 2, 1 total points respectively. The bps system used by FPL has changed from season to season. On analysis, average bps throughout seasons has dropped around 30% from 17/18 to 25/26 season. This will poison models that use bps data to predict a players bonus points received, as the underlying system is inconsistent.

## Decision
Baseline models will ignore bps features for training. For production models, a new feature that calculates the average bps per game of all players in a season can allow models to learn seasonal trends. The feature must only calculate average of matches played up to the target row, to prevent data leakage.

## Notes
- Bps cannot currently be recalculated for past seasons on the current scoring system as data is missing for bps scoring events - e.g. errors leading to a goal, fouls etc.
- New dbt models will be created to calculate seasonal trends

## Considerations
- Extension models proposed in decision 007 to predict point scoring events directly could improve model accuracy for calculating bonus points awarded. Requires further data analysis.