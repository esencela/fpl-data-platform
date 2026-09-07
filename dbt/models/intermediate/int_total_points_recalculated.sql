{{ config(
    alias='total_points_recalculated',
    materialized='table'
)}}

-- Explode scoring rules into long format for easier joining with player stats
with player_stats_long as (
	select
		pg.player_game_key,
		pg.fpl_player_id as player_id,
		ps.season,
		ps.position as fpl_position,
		stat.rule_name,
		stat.stat_value
	from {{ ref('int_player_game_enriched')}} as pg
	join {{ ref('int_player_season_enriched') }} as ps
		on pg.player_season_key = ps.player_season_key
	join {{ ref('defensive_contribution_thresholds') }} as dc
		on ps.position = dc.position
	cross join lateral (
		values
			('goals_scored', pg.goals),
			('assists', pg.assists),
			('clean_sheets', case when pg.clean_sheet then 1 else 0 end),
			('goals_conceded', floor(pg.goals_conceded / 2)::integer), -- FPL awards -1 point for every 2 goals conceded
			('saves', floor(pg.saves / 3)::integer), -- FPL awards 1 point for every 3 saves
			('bonus', pg.bonus),
			('yellow_cards', pg.yellow_cards),
			('red_cards', pg.red_cards),
			('own_goals', pg.own_goals),
			('penalties_saved', pg.penalties_saved),
			('penalties_missed', pg.penalties_taken - pg.penalties_scored),
			('defensive_contribution', case 
											when pg.defensive_contributions >= dc.threshold then 1
											when pg.defensive_contributions is null then null
											else 0 
										end),
			('long_play', case when fpl_minutes >= 60 then 1 else 0 end),
			('short_play', case when fpl_minutes < 60 and game_position is not null then 1 else 0 end)
	) as stat(rule_name, stat_value)
	where stat.stat_value is not null
),

-- Calculate points awarded for each stat based on scoring rules
stats_scored as (
	select
		psl.player_game_key,
		psl.player_id,
		psl.season,
		psl.fpl_position,
		psl.rule_name,
		psl.stat_value,
		coalesce(pos_rule.points, universal_rule.points) as points_per_stat,
		psl.stat_value * coalesce(pos_rule.points, universal_rule.points) as points_awarded
	
	from player_stats_long psl
	left join dev_staging.fpl_scoring_rules as pos_rule
		on psl.rule_name = pos_rule.rule_name
		and psl.fpl_position = pos_rule.position
	left join dev_staging.fpl_scoring_rules as universal_rule
		on psl.rule_name = universal_rule.rule_name
		and universal_rule.position is null
)

select
	player_game_key,
	player_id,
	season,
	sum(points_awarded) as recalculated_points
from stats_scored
group by player_game_key, player_id, season