{{ config(materialized='table') }}

with player_season_totals as (
    select
        player_season_key,
        count(*) as games_total,
        sum(played) as games_played,
        sum(starts) as games_started,
        sum(minutes) as total_minutes,
        sum(goals_scored) as goals,
        sum(assists) as assists,
        sum(goal_involvements) as goal_involvements,
        sum(clean_sheets) as clean_sheets,
        sum(own_goals) as own_goals,
        sum(penalties_saved) as penalties_saved,
        sum(penalties_missed) as penalties_missed,
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
),

player_season_aggregated as (
    select
        *,
        {{ safe_divide('games_started', 'games_played') }} as start_percentage,
        {{ safe_divide('total_minutes', 'games_played') }} as minutes_per_game,
        {{ safe_divide('goals', 'total_minutes') }} * 90 as goals_per_90,
        {{ safe_divide('assists', 'total_minutes') }} * 90 as assists_per_90,
        {{ safe_divide('goal_involvements', 'total_minutes') }} * 90 as goal_involvements_per_90,
        {{ safe_divide('yellow_cards', 'total_minutes') }} * 90 as yellow_cards_per_90,
        {{ safe_divide('red_cards', 'total_minutes') }} * 90 as red_cards_per_90,
        {{ safe_divide('clearances_blocks_interceptions', 'total_minutes') }} * 90 as cbi_per_90,
        {{ safe_divide('recoveries', 'total_minutes') }} * 90 as recoveries_per_90,
        {{ safe_divide('tackles', 'total_minutes') }} * 90 as tackles_per_90,
        {{ safe_divide('defensive_contributions', 'total_minutes') }} * 90 as defcons_per_90,
        {{ safe_divide('saves', 'total_minutes') }} * 90 as saves_per_90,
        {{ safe_divide('total_points', 'games_played') }} as points_per_game,
        {{ safe_divide('bonus', 'games_played') }} as bonus_per_game,
        {{ safe_divide('bps', 'games_played') }} as bps_per_game,
        {{ safe_divide('influence', 'games_played') }} as influence_per_game,
        {{ safe_divide('creativity', 'games_played') }} as creativity_per_game,
        {{ safe_divide('threat', 'games_played') }} as threat_per_game,
        {{ safe_divide('ict_index', 'games_played') }} as ict_index_per_game,
        {{ safe_divide('expected_goals', 'total_minutes') }} * 90 as xg_per_90,
        {{ safe_divide('expected_assists', 'total_minutes') }} * 90 as xa_per_90,
        {{ safe_divide('expected_goal_involvements', 'total_minutes') }} * 90 as xgi_per_90

    from player_season_totals
)

select

    player_season.player_season_key,
    player_season.fpl_player_id as player_id,
    player_season.season,
    player_season.fpl_team_id as team_id,

    season_aggregated.games_total,
    season_aggregated.games_played,
    season_aggregated.games_started,
    season_aggregated.start_percentage,

    season_aggregated.total_minutes,
    season_aggregated.minutes_per_game,
    season_aggregated.goals,
    season_aggregated.goals_per_90,
    season_aggregated.assists,
    season_aggregated.assists_per_90,
    season_aggregated.goal_involvements,
    season_aggregated.goal_involvements_per_90,
    season_aggregated.clean_sheets,
    season_aggregated.own_goals,
    season_aggregated.penalties_saved,
    season_aggregated.penalties_missed,

    season_aggregated.yellow_cards,
    season_aggregated.yellow_cards_per_90,
    season_aggregated.red_cards,
    season_aggregated.red_cards_per_90,

    season_aggregated.clearances_blocks_interceptions,
    season_aggregated.cbi_per_90,
    season_aggregated.recoveries,
    season_aggregated.recoveries_per_90,
    season_aggregated.tackles,
    season_aggregated.tackles_per_90,
    season_aggregated.defensive_contributions,
    season_aggregated.defcons_per_90,
    season_aggregated.saves,
    season_aggregated.saves_per_90,

    season_aggregated.total_points,
    season_aggregated.points_per_game,
    season_aggregated.bonus,
    season_aggregated.bonus_per_game,
    season_aggregated.bps,
    season_aggregated.bps_per_game,

    season_aggregated.influence,
    season_aggregated.influence_per_game,
    season_aggregated.creativity,
    season_aggregated.creativity_per_game,
    season_aggregated.threat,
    season_aggregated.threat_per_game,
    season_aggregated.ict_index,
    season_aggregated.ict_index_per_game,

    season_aggregated.expected_goals,
    season_aggregated.xg_per_90,
    season_aggregated.expected_assists,
    season_aggregated.xa_per_90,
    season_aggregated.expected_goal_involvements,
    season_aggregated.xgi_per_90

from
    {{ ref('int_player_season') }} as player_season
    join {{ ref('dim_player') }} as player
        on player_season.fpl_player_id = player.player_id
    join player_season_aggregated as season_aggregated
        on player_season.player_season_key = season_aggregated.player_season_key