{{ config(
    materialized='view',
    alias='understat_player_game'
) }}

with home_players as (
    select
        match_id,
        key as roster_id,
        value as player_data
    from {{ source('raw', 'understat_match_data') }},
    jsonb_each(raw_data->'rosters'->'h')
),

away_players as (
    select
        match_id,
        key as roster_id,
        value as player_data
    from {{ source('raw', 'understat_match_data') }},
    jsonb_each(raw_data->'rosters'->'a')
),

source_data as (
    select
        *
    from home_players
    union all
    select
        *
    from away_players
)

select
    -- Identifiers
    (player_data->>'id')::int as roster_id,
    match_id::int as match_id,
    (player_data->>'player_id')::int as player_id,
    (player_data->>'team_id')::int as team_id,

    -- Player details
    replace(player_data->>'player', '&#039;', '''') as player_name,
    case
        when player_data->>'h_a' = 'h' then true
        else false
    end as is_home,
    (player_data->>'position') as position,
    (player_data->>'positionOrder')::int as position_order,
    case 
        when (player_data->>'roster_in') = '0' then null
        else (player_data->>'roster_in')::int
    end as replaced_by_roster_id,
    case 
        when (player_data->>'roster_out') = '0' then null
        else (player_data->>'roster_out')::int
    end as replaced_roster_id,

    -- Player stats
    (player_data->>'time')::int as minutes,
    (player_data->>'goals')::int as goals,
    (player_data->>'assists')::int as assists,
    (player_data->>'shots')::int as shots,
    (player_data->>'key_passes')::int as key_passes,
    (player_data->>'own_goals')::int as own_goals,

    -- Discipline
    (player_data->>'yellow_card')::int as yellow_cards,
    (player_data->>'red_card')::int as red_cards,

    -- Expected stats
    (player_data->>'xG')::decimal as expected_goals,
    (player_data->>'xA')::decimal as expected_assists,
    (player_data->>'xGChain')::decimal as expected_goal_chain,
    (player_data->>'xGBuildup')::decimal as expected_goal_buildup

from source_data