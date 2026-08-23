-- weather_dbt/tests/avg_between_min_and_max.sql

select * from {{ ref('daily_city_weather') }}
where avg_temperature_2m < min_temperature_2m
   or avg_temperature_2m > max_temperature_2m
   or avg_relative_humidity_2m < min_relative_humidity_2m
   or avg_relative_humidity_2m > max_relative_humidity_2m
   or avg_wind_speed_10m < min_wind_speed_10m
   or avg_wind_speed_10m > max_wind_speed_10m