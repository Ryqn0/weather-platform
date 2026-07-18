# src/weather_platform/ingestion.py

import requests
from datetime import datetime, timezone


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