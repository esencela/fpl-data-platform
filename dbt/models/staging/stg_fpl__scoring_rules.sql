{{ config(
    alias='fpl_scoring_rules',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select 
        raw_data, 
        season
    from {{ source('raw', 'fpl_bootstrap_static') }}
    order by fetched_at desc
    limit 1
),

source_data as (
    select
        raw_data->'game_config'->'scoring' as scoring,
        season    
    from latest_snapshot
),

rules as (
    select
        season,
        key as rule_name,
        value as rule_value
    
    from source_data,
    jsonb_each(scoring)
),

exploded as (
    select
        season,
        rule_name,
        case
            when jsonb_typeof(rule_value) = 'object'
            then kv.key
            else null
        end as position,
        case
            when jsonb_typeof(rule_value) = 'object'
            then kv.value::numeric
            else rule_value::text::numeric
        end as points  
    from rules
    left join lateral jsonb_each_text(
        case 
            when jsonb_typeof(rule_value) = 'object'
            then rule_value
            else '{}'::jsonb
        end
    ) as kv(key, value)
        on true
    where jsonb_typeof(rule_value) in ('object', 'number')
)

select
    *
from exploded