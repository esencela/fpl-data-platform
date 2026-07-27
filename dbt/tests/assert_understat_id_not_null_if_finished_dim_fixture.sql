select
    fixture_key

from {{ ref('dim_fixture') }}
where understat_fixture_id is null
    and finished = True