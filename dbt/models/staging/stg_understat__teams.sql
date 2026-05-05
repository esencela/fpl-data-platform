{{ config(
    alias='understat_teams',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select
        raw_data,
        season
    from {{ source('raw', 'understat_season_data')}}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'understat_season_data') }})
),

source_data as (
    select
        key as team_id,
        value as team_data
    from latest_snapshot,
    jsonb_each(raw_data->'teams')
)

select
    distinct team_id::int as team_id,
    (team_data->>'title') as team_name

from source_data