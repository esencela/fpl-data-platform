-- Checks whether team_season_id exists for given season in stg_bootstrap_static_teams
{% test team_season_id_exists(model, column_name) %}

select *
from {{ model }} f
left join {{ ref('stg_fpl__teams') }} t
    on f.{{ column_name }} = t.team_season_id
    and f.season = t.season
where t.team_season_id is null

{% endtest %}