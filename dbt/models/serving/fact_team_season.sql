{{ config(materialized='table') }}

with home_games as (
    select
        fixture_key,
        season,
        m.home_team_id as team_id,
        case 
            when m.home_team_score > m.away_team_score then 1
            else 0
        end as win,
        case
            when m.home_team_score = m.away_team_score then 1
            else 0
        end as draw,
        case when m.home_team_score < m.away_team_score then 1
            else 0
        end as loss,
        m.home_team_score as goals_scored,
        m.away_team_score as goals_conceded,
        m.home_expected_goals as expected_goals,
        m.away_expected_goals as expected_goals_against,
        m.home_penalties_scored as penalties_scored,
        m.home_penalties_taken as penalties_taken,
        m.home_influence as influence,
        m.home_creativity as creativity,
        m.home_threat as threat,
        m.home_ict_index as ict_index,
        m.home_yellow_cards as yellow_cards,
        m.home_red_cards as red_cards

    from
        {{ ref('fact_match') }} m
    join {{ ref('dim_fixture') }} using (fixture_key)
),

away_games as (
    select
        fixture_key,
        season,
        m.away_team_id as team_id,
        case 
            when m.away_team_score > m.home_team_score then 1
            else 0
        end as win,
        case
            when m.away_team_score = m.home_team_score then 1
            else 0
        end as draw,
        case when m.away_team_score < m.home_team_score then 1
            else 0
        end as loss,
        m.away_team_score as goals_scored,
        m.home_team_score as goals_conceded,
        m.away_expected_goals as expected_goals,
        m.home_expected_goals as expected_goals_against,
        m.away_penalties_scored as penalties_scored,
        m.away_penalties_taken as penalties_taken,
        m.away_influence as influence,
        m.away_creativity as creativity,
        m.away_threat as threat,
        m.away_ict_index as ict_index,
        m.away_yellow_cards as yellow_cards,
        m.away_red_cards as red_cards
        
    from
        {{ ref('fact_match') }} m
    join {{ ref('dim_fixture') }} using (fixture_key)
),

all_games as (
    select * from home_games
    union all
    select * from away_games
),

season_totals as (
    select
        team_id,
        season,
        count(*) as games_played,
        sum(win) as wins,
        sum(draw) as draws,
        sum(loss) as losses,
        sum(goals_scored) as goals_scored,
        sum(goals_conceded) as goals_against,
        sum(expected_goals) as expected_goals,
        sum(expected_goals_against) as expected_goals_against,
        sum(penalties_scored) as penalties_scored,
        sum(penalties_taken) as penalties_taken,
        sum(influence) as influence,
        sum(creativity) as creativity,
        sum(threat) as threat,
        sum(ict_index) as ict_index,
        sum(yellow_cards) as yellow_cards,
        sum(red_cards) as red_cards

    from all_games
    group by team_id, season
)

select
    team_season.team_season_key,
    team_season.team_id,
    team_season.season,
    games_played,
    wins,
    draws,
    losses,
    goals_scored,
    goals_against,
    goals_scored - goals_against as goal_difference,
    expected_goals,
    expected_goals_against,
    penalties_scored,
    penalties_taken,
    influence,
    creativity,
    threat,
    ict_index,
    yellow_cards,
    red_cards

from 
    {{ ref('int_team_season') }} as team_season
    join season_totals using (team_id, season)
