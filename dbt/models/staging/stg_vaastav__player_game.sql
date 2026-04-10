{{ config(materialized='view') }}

-- Only get data from most recent fetch
with latest_snapshot as (
    select
        raw_data,
        season,
        player_season_id,
        fixture_season_id,
        gameweek_id
    from {{ source('raw', 'vaastav_gws')}}
    where fetched_at = (select max(fetched_at) from {{ source('raw', 'vaastav_gws') }})
)

select
    -- Identifiers
    player_season_id::int as player_season_id,
    season::int as season,
    fixture_season_id::int as fixture_season_id,
    gameweek_id::int as gameweek_id,

    -- Core stats
    (raw_data->>'minutes')::int as minutes,
    (raw_data->>'starts')::int as starts,
    (raw_data->>'goals_scored')::int as goals_scored,
    (raw_data->>'assists')::int as assists,
    (raw_data->>'clean_sheets')::int as clean_sheets,
    (raw_data->>'goals_conceded')::int as goals_conceded,
    (raw_data->>'own_goals')::int as own_goals,

    -- Penalties
    (raw_data->>'penalties_saved')::int as penalties_saved,
    (raw_data->>'penalties_missed')::int as penalties_missed,

    -- Discipline
    (raw_data->>'yellow_cards')::int as yellow_cards,
    (raw_data->>'red_cards')::int as red_cards,

    -- Defensive
    (raw_data->>'clearances_blocks_interceptions')::int as clearances_blocks_interceptions,
    (raw_data->>'recoveries')::int as recoveries,
    (raw_data->>'tackles')::int as tackles,
    (raw_data->>'defensive_contribution')::int as defensive_contributions,
    (raw_data->>'saves')::int as saves,

    -- FPL metrics
    (raw_data->>'total_points')::int as total_points,
    (raw_data->>'bonus')::int as bonus,
    (raw_data->>'bps')::int as bps,
    (raw_data->>'influence')::decimal as influence,
    (raw_data->>'creativity')::decimal as creativity,
    (raw_data->>'threat')::decimal as threat,
    (raw_data->>'ict_index')::decimal as ict_index,
    
    -- Expected metrics
    (raw_data->>'expected_goals')::decimal as expected_goals,
    (raw_data->>'expected_assists')::decimal as expected_assists,
    (raw_data->>'expected_goal_involvements')::decimal as expected_goal_involvements,
    (raw_data->>'expected_goals_conceded')::decimal as expected_goals_conceded, 

    -- Transfer and cost info
    (round((raw_data->>'value')::decimal / 10, 1)) as cost,
    (raw_data->>'selected')::int as selected,
    (raw_data->>'transfers_in')::int as transfers_in,
    (raw_data->>'transfers_out')::int as transfers_out,
    (raw_data->>'transfers_balance')::int as transfers_balance

from latest_snapshot