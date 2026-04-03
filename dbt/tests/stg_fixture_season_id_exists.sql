-- Checks whether fixture_season_id exists for given season in stg_fixtures
{% test fixture_season_id_exists(model, column_name) %}

select *
from {{ model }} f
left join {{ ref('stg_fixtures') }} fx
    on f.{{ column_name }} = fx.fixture_season_id
    and f.season = fx.season
where fx.fixture_season_id is null

{% endtest %}