with players_per_team_per_fixture as (
    select 
        pg.fixture_key,
        pg.at_home,
        count(*) as total_starting
    from {{ ref('int_player_game_enriched') }} pg
    join {{ ref('int_fixtures') }} f
        on pg.fixture_key = f.fixture_key
    where f.finished = true
        and pg.started = true
    group by 
        pg.fixture_key, pg.at_home
)

select
    *
from players_per_team_per_fixture
where total_starting != 11