-- If team has no gametime then team id will not be selected in fact table
with team_ids as (
    select 
        distinct team_id
    from {{ ref('fact_team_season') }}
)

select 
    team_id,
    understat_team_id
from {{ ref('dim_team') }}
where 
    understat_team_id is null
    and team_id in (
        select
            team_id
        from team_ids
    )