{{ config(
    materialized='table',
    alias='all_features'
) }}

select
    -- Identifiers
    player_per_game.player_game_key,
    player_per_game.fixture_key,
    player_per_game.team_id,
    player_per_game.at_home,

    -- Player per game features
    {{ dbt_utils.star(from=ref('ml_player_game_per_game_features'), except=["player_game_key", "fixture_key", "season", "player_id", "team_id", "at_home", "games_played_prior", "shots_taken_prior"]) }},

    -- Player per 90 features
    {{ dbt_utils.star(from=ref('ml_player_game_per_90_features'), except=["player_game_key", "fixture_key", "season", "player_id", "team_id"]) }},

    -- Player form features
    {{ dbt_utils.star(from=ref('ml_player_game_form_features'), except=["player_game_key", "fixture_key", "season", "player_id", "team_id", "games_last_30_days", "minutes_last_30_days"]) }},

    -- Team per game features
    {{ dbt_utils.star(from=ref('ml_team_game_per_game_features'), except=["fixture_key", "team_id", "at_home", "games_played_prior", "opp_games_played_prior"]) }},

    -- Team form features
    {{ dbt_utils.star(from=ref('ml_team_game_form_features'), except=["fixture_key", "team_id", "at_home", "games_played_prior", "opp_games_played_prior"]) }}

from {{ ref('ml_player_game_per_game_features') }} player_per_game
join {{ ref('ml_player_game_per_90_features') }} player_per_90
    on player_per_game.player_game_key = player_per_90.player_game_key
join {{ ref('ml_player_game_form_features') }} player_form
    on player_per_game.player_game_key = player_form.player_game_key
join {{ ref('ml_team_game_per_game_features') }} team_per_game
    on player_per_game.fixture_key = team_per_game.fixture_key
    and player_per_game.team_id = team_per_game.team_id
join {{ ref('ml_team_game_form_features') }} team_form
    on player_per_game.fixture_key = team_form.fixture_key
    and player_per_game.team_id = team_form.team_id