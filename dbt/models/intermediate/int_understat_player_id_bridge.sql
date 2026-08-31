{{ config(
    alias='understat_player_id_bridge',
    materialized='table'
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
)

select
    *
from add_understat_match_id