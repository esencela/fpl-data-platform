{{ config(materialized='view') }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select
        raw_data,
        season
    from {{ source('raw', 'fpl_element_summary')}}
),

source_data as (
    select
        jsonb_array_elements(raw_data->'history') as player_game,
        season
    from latest_snapshot
)

select
    -- Identifiers
    (player_game->>'element')::int as player_season_id,
    season::int as season,
    (player_game->>'fixture')::int as fixture_season_id,
    
    -- Core stats
    (player_game->>'minutes')::int as minutes,
    (player_game->>'starts')::int as starts,
    (player_game->>'goals_scored')::int as goals_scored,
    (player_game->>'assists')::int as assists,
    (player_game->>'clean_sheets')::int as clean_sheets,
    (player_game->>'goals_conceded')::int as goals_conceded,
    (player_game->>'own_goals')::int as own_goals,
    
    -- Penalties
    (player_game->>'penalties_saved')::int as penalties_saved,
    (player_game->>'penalties_missed')::int as penalties_missed,

    -- Discipline
    (player_game->>'yellow_cards')::int as yellow_cards,
    (player_game->>'red_cards')::int as red_cards,

    -- Defensive
    (player_game->>'clearances_blocks_interceptions')::int as clearances_blocks_interceptions,
    (player_game->>'recoveries')::int as recoveries,
    (player_game->>'tackles')::int as tackles,
    (player_game->>'defensive_contribution')::int as defensive_contributions,
    (player_game->>'saves')::int as saves,

    -- FPL metrics
    (player_game->>'total_points')::int as total_points,
    (player_game->>'bonus')::int as bonus,
    (player_game->>'bps')::int as bps,
    (player_game->>'influence')::decimal as influence,
    (player_game->>'creativity')::decimal as creativity,
    (player_game->>'threat')::decimal as threat,
    (player_game->>'ict_index')::decimal as ict_index,
    
    -- Expected metrics
    (player_game->>'expected_goals')::decimal as expected_goals,
    (player_game->>'expected_assists')::decimal as expected_assists,
    (player_game->>'expected_goal_involvements')::decimal as expected_goal_involvements,
    (player_game->>'expected_goals_conceded')::decimal as expected_goals_conceded, 

    -- Transfer and cost info
    (round((player_game->>'value')::decimal / 10, 1)) as cost,
    (player_game->>'selected')::int as selected,
    (player_game->>'transfers_in')::int as transfers_in,
    (player_game->>'transfers_out')::int as transfers_out,
    (player_game->>'transfers_balance')::int as transfers_balance

from source_data