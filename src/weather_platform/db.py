# src/weather_platform/db.py

from weather_platform.config import get_connection

def get_or_create_location(cur, country: str, city: str, latitude: float, longitude: float) -> int:
    """
    Helper function that will get the location_id when upserting so will create if it already exists
    Args:
        cur: Cursor for the connection method with psycopg
        country: Name of country
        city: Name of city
        latitude: Latitude coordinate of the city
        longitude: Longitude coordinate of the city
    Return:
        location_id which is an int
    """

    cur.execute("""
            INSERT INTO locations (country, city, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (country, city) DO UPDATE SET latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude
            RETURNING location_id;
                """, [country, city, latitude, longitude])
    
    #  print(cur.fetchone()[0])
    
    return cur.fetchone()[0]


def load_records(records: list[dict]):
        """
        Load the data into datasets
        """
        
        with get_connection() as conn:

            with conn.cursor() as cur:

                for record in records:

                    location_id = get_or_create_location(cur, record["country"], record["city"], record["latitude"], record["longitude"])
                    # print(location_id)
                    cur.execute("""
                        INSERT INTO weather_readings (location_id, observed_at, ingested_at, temperature_2m, relative_humidity_2m, wind_speed_10m)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (location_id, observed_at) DO NOTHING;
                            """, [location_id, record["observed_at"], record["ingested_at"], record["temperature_2m"], record["relative_humidity_2m"], record["wind_speed_10m"]])