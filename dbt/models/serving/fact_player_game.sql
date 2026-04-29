{{ config(materialized='table') }}

select
    -- Identifiers
    player_game.player_game_key,
    player.fpl_player_id as player_id,
    player.player_season_key,
    case
        when player_game.at_home then fixture.home_team_id
        else fixture.away_team_id
    end as team_id,
    player_game.fixture_key,
    extract(date from fixture.kickoff_time) as date_key,

    -- Game details
    case -- Some players have zero minutes but have still played
        when (player_game.minutes > 0 or
              player_game.starts > 0 or
              player_game.influence > 0 or
              player_game.creativity > 0 or
              player_game.threat > 0 or
              player_game.ict_index > 0 or
              player_game.bps > 0
              ) then 1
        else 0
    end as played,    
    player_game.starts,
    player_game.at_home,
    player_game.minutes,

    -- Base stats
    player_game.goals_scored,
    player_game.assists,
    player_game.goals_scored + player_game.assists as goal_involvements,
    player_game.goals_conceded,
    player_game.clean_sheets,
    player_game.own_goals,
    player_game.penalties_saved,
    player_game.penalties_missed,

    -- Discipline
    player_game.yellow_cards,
    player_game.red_cards,

    -- Defensive stats
    player_game.clearances_blocks_interceptions,
    player_game.recoveries,
    player_game.tackles,
    player_game.defensive_contributions,
    player_game.saves,

    -- FPL points
    player_game.total_points,
    player_game.bonus,
    player_game.bps,

    -- FPL metrics
    player_game.influence,
    player_game.creativity,
    player_game.threat,
    player_game.ict_index,

    -- Expected stats
    player_game.expected_goals,
    player_game.expected_assists,
    player_game.expected_goal_involvements,

    -- FPL metrics
    player_game.cost,
    player_game.selected,
    player_game.transfers_in,
    player_game.transfers_out,
    player_game.transfers_balance,

    -- Metadata
    player_game.missing_starts_flag

from
    {{ ref('int_player_game') }} as player_game
    join {{ ref('int_player_season') }} as player
        on player_game.player_season_key = player.player_season_key
    join {{ ref('dim_fixture') }} as fixture
        on player_game.fixture_key = fixture.fixture_key