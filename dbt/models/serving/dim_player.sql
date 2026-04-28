{{ config(materialized='table')}}

-- Only collect player information from most recent season
with season_ranked as (
    select
        fpl_player_id,
        first_name,
        second_name,
        known_name,
        web_name,
        birth_date,
        country_id,
        row_number() over (
            partition by fpl_player_id
            order by season desc
        ) as rn
    from {{ ref('int_player_season')}}
)

select
    fpl_player_id as player_id,
    first_name,
    second_name,
    known_name,
    web_name,
    birth_date
from season_ranked
where rn = 1