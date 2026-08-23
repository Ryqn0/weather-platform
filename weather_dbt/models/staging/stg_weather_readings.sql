-- weather_dbt/models/staging/stg_weather_readings.sql

select

    r.location_id as location_id,
    l.country as country,
    l.city as city,
    r.observed_at as observed_at,
    r.ingested_at as ingested_at,
    r.temperature_2m as temperature_2m,
    r.relative_humidity_2m as relative_humidity_2m,
    r.wind_speed_10m as wind_speed_10m

from {{ source('raw', 'weather_readings') }} r

join {{ source('raw', 'locations') }} l using (location_id)