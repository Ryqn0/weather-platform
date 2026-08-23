-- weather_dbt/models/marts/daily_city_weather.sql

select

    country,
    city,
    date_trunc('day', observed_at) as weather_date,
    avg(temperature_2m) as avg_temperature_2m,
    min(temperature_2m) as min_temperature_2m,
    max(temperature_2m) as max_temperature_2m,
    avg(relative_humidity_2m) as avg_relative_humidity_2m,
    min(relative_humidity_2m) as min_relative_humidity_2m,
    max(relative_humidity_2m) as max_relative_humidity_2m,
    avg(wind_speed_10m) as avg_wind_speed_10m,
    min(wind_speed_10m) as min_wind_speed_10m,
    max(wind_speed_10m) as max_wind_speed_10m

from {{ ref('stg_weather_readings') }}

{{ dbt_utils.group_by(3) }}