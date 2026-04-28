{{ config(materialized='table') }}

{{ dbt_date.get_date_dimension("2016-01-01", "2035-12-31") }}