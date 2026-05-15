{{ config(materialized='table') }}

select
    team_id,
    understat_team_id,
    team_name,
    short_name
from {{ ref('int_team_season') }}
group by
    team_id,
    understat_team_id,
    team_name,
    short_name