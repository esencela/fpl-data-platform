{{ config(
    alias='team_fixture_spine',
    materialized='table'
) }}

with home_games as (
    select
        f.fixture_key,
        f.season,
        f.home_team_id as team_id,
        true as at_home,
        f.kickoff_time,
        f.finished
    from {{ ref('dim_fixture') }} f
),

away_games as (
    select
        f.fixture_key,
        f.season,
        f.away_team_id as team_id,
        false as at_home,
        f.kickoff_time,
        f.finished
    from {{ ref('dim_fixture') }} f
)

select *
from home_games
union all
select *
from away_games