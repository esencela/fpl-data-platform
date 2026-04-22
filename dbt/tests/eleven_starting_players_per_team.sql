with players_per_team_per_fixture as (
    select 
        fixture_key,
        at_home,
        sum(starts) as total_starting
    from {{ ref('int_player_game') }}
    group by 
        fixture_key, at_home
)

select
    *
from players_per_team_per_fixture
where total_starting != 11