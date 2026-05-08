{{ config(
    materialized='view',
    alias='id_mappings'
) }}

with latest_snapshot as (
    select
        code,
        raw_data,
        fetched_at,
        row_number() over (partition by code order by fetched_at desc) as rn

    from {{ source('raw', 'id_mappings') }}
)

select
    code::int as fpl_player_id,
    ((raw_data->>'understat')::numeric)::int as understat_id,
    raw_data->>'fbref' as fbref_id,
    (raw_data->>'transfermarkt')::int as transfermarkt_id,
    (raw_data->>'whoscored')::int as whoscored_id

from latest_snapshot
where rn = 1