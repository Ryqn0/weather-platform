CREATE TABLE locations (
    location_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    UNIQUE (country, city)
);

CREATE TABLE weather_readings (
    ingested_at timestamptz NOT NULL,
    location_id bigint NOT NULL REFERENCES locations (location_id),
    observed_at timestamptz NOT NULL,
    temperature_2m real NOT NULL,
    relative_humidity_2m integer NOT NULL,
    wind_speed_10m real NOT NULL,
    PRIMARY KEY (location_id, observed_at)
);

