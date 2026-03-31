{{ config(materialized='view') }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select raw_data
    from {{ source('raw', 'bootstrap_static') }}
    order by fetched_at desc
    limit 1
),

source_data as (
    select jsonb_array_elements(raw_data->'teams') as team
    from latest_snapshot
)

select 
    (team->>'code')::int as team_id,
    (team->>'id')::int as team_season_id,
    team->>'name' as name,
    team->>'short_name' as short_name,
    team->>'strength_overall_home' as strength_overall_home,
    team->>'strength_overall_away' as strength_overall_away,
    team->>'strength_attack_home' as strength_attack_home,
    team->>'strength_attack_away' as strength_attack_away,
    team->>'strength_defence_home' as strength_defence_home,
    team->>'strength_defence_away' as strength_defence_away
from source_data

