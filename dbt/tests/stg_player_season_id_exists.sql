-- Checks whether player_season_id exists for given season in stg_bootstrap_static_players
{% test player_season_id_exists(model, column_name) %}

select *
from {{ model }} f
left join {{ ref('stg_fpl__players') }} p
    on f.{{ column_name }} = p.player_season_id
    and f.season = p.season
where p.player_season_id is null

{% endtest %}