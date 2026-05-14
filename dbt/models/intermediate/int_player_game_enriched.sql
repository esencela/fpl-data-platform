{{ config(
    alias='player_game_enriched',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_game_key']
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

-- Merge understat data through id
join_understat as (
    select
        -- Player Identifiers
        fpl.player_game_key,
        fpl.player_season_key,
        fpl.fpl_player_id,
        fpl.fpl_player_season_id,
        understat.roster_id as understat_roster_id,
        understat.player_id as understat_player_id,
        understat.team_id as understat_team_id,

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
        understat.minutes,
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
        fpl.clean_sheets,
        fpl.goals_conceded,
        fpl.own_goals,

        -- Discipline
        fpl.yellow_cards,
        fpl.red_cards,

        -- Defensive stats
        fpl.clearances_blocks_interceptions,
        fpl.recoveries,
        fpl.tackles,
        fpl.defensive_contributions,
        fpl.saves,
        fpl.penalties_saved,

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

    from add_understat_match_id fpl
    left join {{ ref('stg_understat__player_game') }} understat
        on fpl.understat_player_id = understat.player_id
        and fpl.understat_fixture_id = understat.match_id
)

select *
from join_understat