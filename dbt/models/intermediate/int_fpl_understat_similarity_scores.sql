{{ config(
    alias='fpl_understat_similarity_scores',
    materialized='table'
) }}

-- Cross join all possible name candidates from fpl data and normalize (lower case and replace accented letters)
with fpl_name_candidates as (
    select
        fpl.fpl_player_id,
        fpl.understat_team_id,
        fpl.understat_fixture_id,
        candidate.name_type,
        normalize_player_name(candidate.name_value) as norm_name

    from {{ ref('int_fpl_players_missing_understat_id') }} fpl
    cross join lateral (
        values
            ('known_name',  fpl.known_name),
            ('web_name',    fpl.web_name),
            ('full_name',   fpl.first_name || ' ' || fpl.second_name),
            ('first_name',  fpl.first_name),
            ('second_name', fpl.second_name)
    ) as candidate(name_type, name_value)
    where candidate.name_value is not null
      and trim(candidate.name_value) <> ''
),

-- Select all unmapped understat players and normalize name (lower case and replace accented letters)
unmapped_understat_players as (
	select
		player_id as understat_player_id,
		team_id as understat_team_id,
		match_id as understat_fixture_id,
		normalize_player_name(player_name) as norm_name
	from {{ ref('int_unmapped_understat_players') }}
),

-- Create similarity scores on all id pairings with matching team and fixture
similarity_scores as (
	select
		f.fpl_player_id,
		u.understat_player_id,
		f.norm_name as fpl_norm_name,
		u.norm_name as understat_norm_name,
		f.name_type,
		similarity(f.norm_name, u.norm_name) as similarity
	from fpl_name_candidates f
	join unmapped_understat_players u
		on f.understat_team_id = u.understat_team_id
		and f.understat_fixture_id = u.understat_fixture_id
),

-- Rank pairings on similarity score
ranked_pairs as (
	select
		fpl_player_id,
		understat_player_id,
		fpl_norm_name,
		name_type,
		understat_norm_name,
		similarity,
		row_number() over (
			partition by fpl_player_id
			order by similarity desc
		) as rank
	from similarity_scores
)

select *
from ranked_pairs