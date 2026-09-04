# 007 - FPL points system changed

## Context
The method that FPL uses to calculate points changes throughout seasons - e.g. Goals upgraded from 4 to 5 points, defensive contributions added as point scoring events. This will poison any model that predicts total points directly as the underlying system is inconsistent.

## Decision
New labels will be calculated for all player game rows based on the current season points scoring system, which is provided in extracted FPL data. These can then be used for baseline models or further models that use total points as a target variable.

## Notes
- Defensive Contributions data is missing for 19/20 to 24/25 seasons. This will reduce the amount of training data we have.
- New dbt models will be created to store fpl scoring system data

## Considerations
- Extension models can be developed that predict the chance of point scoring events directly - e.g. goals, assists, defensive contributions. This could eliminate the need for recalculating for previous seasons.