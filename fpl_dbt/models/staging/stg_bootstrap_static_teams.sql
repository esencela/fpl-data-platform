{{ config(materialized='view') }}

with source_data as (
    select jsonb_array_elements(raw_data->'teams') as team
    from {{ source('raw', 'bootstrap_static') }}
)

select 
    (team->>'code')::int as team_id,
    (team->>'id')::int as season_team_id,
    team->>'name' as name,
    team->>'short_name' as short_name,
    team->>'strength_overall_home' as strength_overall_home,
    team->>'strength_overall_away' as strength_overall_away,
    team->>'strength_attack_home' as strength_attack_home,
    team->>'strength_attack_away' as strength_attack_away,
    team->>'strength_defence_home' as strength_defence_home,
    team->>'strength_defence_away' as strength_defence_away
from source_data

