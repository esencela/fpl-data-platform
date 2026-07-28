{{ config(
    alias='player_game_enriched',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_game_key'],
    on_schema_change='append_new_columns'
)}}

-- Join fpl player id from base
with add_player_id as (
    select
        game.*,
        season.fpl_player_id
    from {{ ref('int_player_game_base') }} game
    left join {{ ref('int_player_season_base') }} season
        on game.player_season_key = season.player_season_key
),

-- Fix inconsistent fpl player ids
id_map as (
    select
        *
    from add_player_id base
    left join {{ ref('fpl_player_id_map') }} map
        on base.fpl_player_id = map.from_player_id
),

id_fixed as (
    select
        *,
        coalesce(to_player_id, fpl_player_id) as canon_fpl_player_id
    from id_map
),

-- Join understat ids
add_understat_player_id as (
    select
        s.*,
        map.understat_id as understat_player_id
    from id_fixed s
    left join {{ ref('int_player_id_map') }} map
        on s.canon_fpl_player_id = map.fpl_player_id
),

-- Add understat match id for merging
add_understat_match_id as (
    select
        pg.*,
        fixture.understat_fixture_id
    from add_understat_player_id pg
    join {{ ref('int_fixtures') }} fixture
        on pg.fixture_key = fixture.fixture_key
),

-- Aggregate penalty data for each player-game
penalty_data as (
    select
        fixture_key,
        fpl_player_id,
        count(*) as penalties_taken,
        sum(case when outcome = 'Goal' then 1 else 0 end) as penalties_scored
    from {{ ref('int_shots') }}
    where situation = 'Penalty'
    group by
        fixture_key,
        fpl_player_id
),

-- Join penalty data
joined_penalty_data as (
    select
        player.*,
        penalty.penalties_taken,
        penalty.penalties_scored
    from add_understat_match_id player
    left join penalty_data penalty
        on player.fixture_key = penalty.fixture_key
        and player.fpl_player_id = penalty.fpl_player_id
),

-- Merge understat data through id
join_understat as (
    select
        -- Player Identifiers
        fpl.player_game_key,
        fpl.player_season_key,
        fpl.canon_fpl_player_id as fpl_player_id,
        fpl.fpl_player_season_id,
        understat.roster_id as understat_roster_id,
        fpl.understat_player_id,

        -- Match identifiers
        fpl.season,
        fpl.fixture_key,
        fpl.fpl_fixture_season_id,
        fpl.understat_fixture_id,
        fpl.gameweek_id,

        -- Match info
        fpl.at_home,
        understat.position as game_position,
        understat.replaced_by_roster_id,
        understat.replaced_roster_id,

        -- Core stats
        case
            when understat.position_order is not null and understat.position_order != 17 then true
            else false
        end as started,
        case    
            when understat.minutes is null then 0
            else understat.minutes
        end as minutes,
        fpl.goals_scored as goals,
        fpl.assists,
        case
            when understat.shots is null then 0
            else understat.shots
        end as shots,
        case
            when understat.key_passes is null then 0
            else understat.key_passes
        end as key_passes,
        case 
            when fpl.clean_sheets = 0 then false
            else true
        end as clean_sheet,
        fpl.goals_conceded,
        fpl.own_goals,

        -- Discipline
        fpl.yellow_cards,
        fpl.red_cards,

        -- Penalties
        case
            when fpl.penalties_scored is null then 0
            else fpl.penalties_scored
        end as penalties_scored,
        case
            when fpl.penalties_taken is null then 0
            else fpl.penalties_taken
        end as penalties_taken,
        fpl.penalties_saved,

        -- Defensive stats
        fpl.clearances_blocks_interceptions,
        fpl.recoveries,
        fpl.tackles,
        fpl.defensive_contributions,
        fpl.saves,        

        -- Expected metrics
        case
            when understat.expected_goals is null then 0
            else understat.expected_goals
        end as expected_goals,
        case
            when understat.expected_assists is null then 0
            else understat.expected_assists
        end as expected_assists,
        case
            when understat.expected_goal_chain is null then 0
            else understat.expected_goal_chain
        end as expected_goal_chain,
        case
            when understat.expected_goal_buildup is null then 0
            else understat.expected_goal_buildup
        end as expected_goal_buildup,

        -- FPL metrics
        fpl.total_points,
        fpl.bonus,
        fpl.bps,
        fpl.influence,
        fpl.creativity,
        fpl.threat,
        fpl.ict_index,

        -- Transfer and cost info
        fpl.cost,
        fpl.selected,
        fpl.transfers_in,
        fpl.transfers_out,
        fpl.transfers_balance

    from joined_penalty_data fpl
    left join {{ ref('stg_understat__player_game') }} understat
        on fpl.understat_player_id = understat.player_id
        and fpl.understat_fixture_id = understat.match_id
)

select *
from join_understat