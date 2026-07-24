{{ config(materialized='table') }}

with ranked as (
    select
        team_id,
        understat_team_id,
        team_name,
        short_name,
        row_number() over (
            partition by team_id
            order by season desc
        ) as r

        from {{ ref('int_team_season') }}
)

select
    team_id,
    understat_team_id,
    team_name,
    short_name
from ranked
where r = 1