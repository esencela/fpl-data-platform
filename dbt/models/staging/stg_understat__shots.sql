{{ config(
    alias='understat_shots',
    materialized='view'
) }}

with home_shots as (
    select
        match_id,
        jsonb_array_elements(raw_data->'h') as shot_data
    from {{ source('raw', 'understat_shot_data') }}
),

away_shots as (
    select
        match_id,
        jsonb_array_elements(raw_data->'a') as shot_data
    from {{ source('raw', 'understat_shot_data') }}
),

source_data as (
    select
        *
    from home_shots
    union all
    select
        *
    from away_shots
)

select
    -- Identifiers
    (shot_data->>'id')::int as shot_id,
    (shot_data->>'season')::int + 1 as season, -- Understat seasons use start year, we use end year
    (shot_data->>'match_id')::int as match_id,
    (shot_data->>'player_id')::int as player_id,
    replace(shot_data->>'player', '&#039;', '''') as player_name,
    case
        when shot_data->>'h_a' = 'h' then (shot_data->>'h_team')
        else (shot_data->>'a_team')
    end as team_name,
    case 
        when shot_data->>'h_a' = 'h' then true
        else false
    end as is_home,

    -- Shot details
    (shot_data->>'minute')::int as minute,
    shot_data->>'situation' as situation,
    shot_data->>'shotType' as shot_type,
    shot_data->>'result' as outcome,
    replace(shot_data->>'player_assisted', '&#039;', '''') as player_assisted,
    shot_data->>'lastAction' as last_action,
    (shot_data->>'xG')::decimal as expected_goals,
    (shot_data->>'X')::decimal as x,
    (shot_data->>'Y')::decimal as y

from 
    source_data