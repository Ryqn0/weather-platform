# main.py

import requests
import json
from pathlib import Path
from datetime import datetime, timezone
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()


def fetch_current_weather(latitude: float, longitude: float) -> dict:
    """
    Call Open-Meteo and return the parsed JSON response as a dict
    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
    Returns:
        dict: Parsed JSON response from Open-Meteo
    """

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
    }

    try:

        response = requests.get(url=url, params=params, timeout=5)
        # print(response)
        response.raise_for_status()
        response_dict = response.json()
        # print(response_dict)
        
        return response_dict

    except requests.exceptions.HTTPError as e:

        print("HTTP error occurred:", e)

        return {'error_status': str(e)}

    except requests.exceptions.RequestException as e:

        print("A request error occurred:", e)

        return {'error_status': str(e)}


def save_raw(data: dict, path: str) -> None:
    """
    Write the dict to a JSON file at 'path'
    Args:
        data: The dict to save
        path: The path where to save
    """

    file_path = Path(path).with_suffix(".json")
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(data, f)


def fetch_many(cities: list[dict]) -> list[dict]:
    """
    Fetch current weather for every city, return one clean record per city
    Args:
        cities: List of dict with city name, longitude and latitude
    Return:
        list of dicts with informations on city weather
    """

    list_many = []

    for city in cities:
        city_resp = fetch_current_weather(city['latitude'], city['longitude'])
        # print(type(city_resp["current"]["time"]))
        record = {
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "country": city["country"],
            "city": city["city"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "observed_at": datetime.fromisoformat(city_resp["current"]["time"]).replace(tzinfo=timezone.utc).isoformat(),
            "temperature_2m": city_resp["current"]["temperature_2m"],
            "relative_humidity_2m": city_resp["current"]["relative_humidity_2m"],
            "wind_speed_10m": city_resp["current"]["wind_speed_10m"]
        }
        list_many.append(record)

    return list_many


def connection_test():
    """
    Testing the connection with the database
    """

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT version();
                        """)
            
            print(cur.fetchone())

# COLUMNS = ["ingested_at", "country", "city", "latitude", "longitude", "observed_at", "temperature_2m", "relative_humidity_2m", "wind_speed_10m"]


# def insert_records(records: list[dict]) -> None:
#     """
#     Insert records into the Postgresql database
#     Args:
#         records: list of dicts of the record to inserts
#     """

#     with get_connection() as conn:

#         with conn.cursor() as cur:

#             # print([tuple(record[c] for c in record.keys()) for record in records])
            
#             cur.executemany("""
#                 INSERT INTO "weather_readings" (ingested_at, country, city, latitude, longitude, observed_at, temperature_2m, relative_humidity_2m, wind_speed_10m) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                             ON CONFLICT (country, city, observed_at) DO NOTHING;
#                         """, [tuple(record[c] for c in COLUMNS) for record in records])
            

def get_connection():

    return psycopg.connect(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"))


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



def main():

    dicts_to_test = [{"country": "France", "city": "Paris", "latitude": 48.85, "longitude": 2.35}, {"country": "China", "city": "Shanghai", "latitude": 31.22, "longitude": 121.46},
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21}]
    jsondict = fetch_many(dicts_to_test)
    # save_raw(jsondict, "data/testing/weather.json")

    #insert_records(jsondict)
    with get_connection() as conn:

        with conn.cursor() as cur:

            response_list = fetch_many(dicts_to_test)

            for response_dict in response_list:

                # print(dicto)
                
                # print(response_dict)
                location_id = get_or_create_location(cur, response_dict["country"], response_dict["city"], response_dict["latitude"], response_dict["longitude"])
                # print(location_id)
                cur.execute("""
                        INSERT INTO weather_readings (location_id, observed_at, ingested_at, temperature_2m, relative_humidity_2m, wind_speed_10m)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (location_id, observed_at) DO NOTHING;
                            """, [location_id, response_dict["observed_at"], response_dict["ingested_at"], response_dict["temperature_2m"], response_dict["relative_humidity_2m"], response_dict["wind_speed_10m"]])

    # connection_test()





if __name__ == "__main__":
    main()
