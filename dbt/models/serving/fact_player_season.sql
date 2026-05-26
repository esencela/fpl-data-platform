{{ config(materialized='table') }}

with player_season_totals as (
    select
        player_season_key,
        count(*) as games_total,
        sum(case when played then 1 else 0 end) as games_played,
        sum(case when started then 1 else 0 end) as games_started,
        sum(minutes) as total_minutes,
        sum(goals) as goals,
        sum(assists) as assists,
        sum(goal_involvements) as goal_involvements,
        sum(case when clean_sheet then 1 else 0 end) as clean_sheets,
        sum(own_goals) as own_goals,
        sum(penalties_scored) as penalties_scored,
        sum(penalties_taken) as penalties_taken,
        sum(penalties_saved) as penalties_saved,
        sum(yellow_cards) as yellow_cards,
        sum(red_cards) as red_cards,
        sum(clearances_blocks_interceptions) as clearances_blocks_interceptions,
        sum(recoveries) as recoveries,
        sum(tackles) as tackles,
        sum(defensive_contributions) as defensive_contributions,
        sum(saves) as saves,
        sum(total_points) as total_points,
        sum(bonus) as bonus,
        sum(bps) as bps,
        sum(influence) as influence,
        sum(creativity) as creativity,
        sum(threat) as threat,
        sum(ict_index) as ict_index,
        sum(expected_goals) as expected_goals,
        sum(expected_assists) as expected_assists,
        sum(expected_goal_involvements) as expected_goal_involvements

    from {{ ref('fact_player_game') }}
    group by player_season_key
)

select
    player_season.player_season_key,
    player_season.fpl_player_id as player_id,
    player_season.season,
    player_season.fpl_team_id as team_id,

    totals.games_total,
    totals.games_played,
    totals.games_started,

    totals.total_minutes,
    totals.goals,
    totals.assists,
    totals.goal_involvements,
    totals.clean_sheets,
    totals.own_goals,    

    totals.yellow_cards,
    totals.red_cards,
    
    totals.penalties_scored,
    totals.penalties_taken,
    totals.penalties_saved,

    totals.clearances_blocks_interceptions,
    totals.recoveries,
    totals.tackles,
    totals.defensive_contributions,
    totals.saves,

    totals.total_points,
    totals.bonus,
    totals.bps,

    totals.influence,
    totals.creativity,
    totals.threat,
    totals.ict_index,

    totals.expected_goals,
    totals.expected_assists,
    totals.expected_goal_involvements

from
    {{ ref('int_player_season_enriched') }} as player_season
    join player_season_totals as totals
        on player_season.player_season_key = totals.player_season_key