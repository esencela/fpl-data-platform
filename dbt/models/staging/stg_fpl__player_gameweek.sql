{{ config(
    alias='fpl_player_gameweek',
    materialized='view'
) }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select 
        raw_data,
        season,
        gameweek_id
    from {{ source('raw', 'fpl_events') }}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'fpl_events') }})
),

source_data as (
    select 
        jsonb_array_elements(raw_data->'elements') as event,
        season,
        gameweek_id
    from latest_snapshot
),

flattened as (
    select
        (event->>'id')::int as player_season_id,
        season,
        gameweek_id,
        event->'stats' as stats
    from source_data
)

select
    gameweek_id::int as gameweek_id,
    season::int as season,
    player_season_id,

    -- Core stats
    (stats->>'minutes')::int as minutes,
    (stats->>'starts')::int as starts,
    (stats->>'goals_scored')::int as goals_scored,
    (stats->>'assists')::int as assists,
    (stats->>'clean_sheets')::int as clean_sheets,
    (stats->>'goals_conceded')::int as goals_conceded,
    (stats->>'own_goals')::int as own_goals,
    
    -- Penalties
    (stats->>'penalties_saved')::int as penalties_saved,
    (stats->>'penalties_missed')::int as penalties_missed,

    -- Discipline
    (stats->>'yellow_cards')::int as yellow_cards,
    (stats->>'red_cards')::int as red_cards,

    -- Defensive
    (stats->>'clearances_blocks_interceptions')::int as clearances_blocks_interceptions,
    (stats->>'recoveries')::int as recoveries,
    (stats->>'tackles')::int as tackles,
    (stats->>'defensive_contribution')::int as defensive_contributions,
    (stats->>'saves')::int as saves,

    -- FPL metrics
    (stats->>'total_points')::int as total_points,
    (stats->>'bonus')::int as bonus,
    (stats->>'bps')::int as bps,
    (stats->>'influence')::decimal as influence,
    (stats->>'creativity')::decimal as creativity,
    (stats->>'threat')::decimal as threat,
    (stats->>'ict_index')::decimal as ict_index,
    
    -- Expected metrics
    (stats->>'expected_goals')::decimal as expected_goals,
    (stats->>'expected_assists')::decimal as expected_assists,
    (stats->>'expected_goal_involvements')::decimal as expected_goal_involvements,
    (stats->>'expected_goals_conceded')::decimal as expected_goals_conceded    

from flattened