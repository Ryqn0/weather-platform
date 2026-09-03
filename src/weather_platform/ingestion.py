# src/weather_platform/ingestion.py

import asyncio
import httpx
from datetime import datetime, timezone
import logging
import os

from weather_platform.validation import is_valid_record
from weather_platform.storage import save_raw_to_gcs
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")

logger = logging.getLogger(__name__)


async def fetch_current_weather(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, latitude: float, longitude: float) -> dict:
    """
    Call Open-Meteo by awaiting the api call using a shared client and return the parsed JSON response as a dict
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

        logger.info("Starting fetching of the current weather...")

        logger.debug("latitude : %s and longitude : %s ...", latitude, longitude)

        async with semaphore:

            response = await client.get(url=url, params=params, timeout=5)

            logger.debug("Response : %s", response)

            # print(response)
            response.raise_for_status()
            response_dict = response.json()
            # print(response_dict)

            logger.debug("Response JSON format : %s", response_dict)

            logger.info("Fetch of current weather succesful!")
            
            return response_dict

    except httpx.HTTPStatusError as e:

            logger.warning("HTTP status error occured : %s", e)

            # print("HTTP status error occured:", e)
    
            return {'error_status': str(e)}

    except httpx.RequestError as e:

            logger.warning("A request error occurred : %s", e)

            # print("A request error occurred:", e)
    
            return {'error_status': str(e)}

    except httpx.HTTPError as e:

        logger.warning("HTTP error occurred : %s", e)

        # print("HTTP error occurred:", e)

        return {'error_status': str(e)}


def build_partitioned_object_path() -> str:
    """Helper function that create the partitioned object path using UTC timestamp"""

    
    date = datetime.now(timezone.utc)
    logger.debug(f"Datetime is %s", date)

    stamp = date.strftime("%Y%m%dT%H%M%SZ")
    logger.debug(f"Stamp is %s", stamp)

    return f"raw/weather/year={date.year}/month={date.month:02d}/day={date.day:02d}/{stamp}.json"
    

async def fetch_many(cities: list[dict]) -> list[dict]:
    """
    Fetch current weather for every city, return one clean record per city
    Args:
        cities: List of dict with city name, longitude and latitude
    Return:
        list of dicts with informations on city weather
    """

    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient() as client:

        logger.info("Starting fetching from the list of cities...")

        logger.debug("List of cities : %s ...", cities)

        responses = await asyncio.gather(*[
            fetch_current_weather(client, semaphore, c['latitude'], c['longitude']) for c in cities
        ])

        logger.debug("Responses : %s", responses)

        logger.info("Finished fetching of the list!")

    # print(responses) # debug

    logger.info("Starting the formating into a list of record of all cities...")

    records = []

    for city, resp in zip(cities, responses):

        if "current" not in resp:

            logger.warning("Skipping %s: no valid data in response", city["city"])

            continue

        record = {
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "country": city["country"],
            "city": city["city"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "observed_at": datetime.fromisoformat(resp["current"]["time"]).replace(tzinfo=timezone.utc).isoformat(),
            "temperature_2m": resp["current"]["temperature_2m"],
            "relative_humidity_2m": resp["current"]["relative_humidity_2m"],
            "wind_speed_10m": resp["current"]["wind_speed_10m"]
        }

        if not is_valid_record(record):

            logger.warning("Rejecting %s: failed validation", city)

            continue

        records.append(record)

    # save_raw_to_gcs(responses, BUCKET_NAME, build_partitioned_object_path())

    logger.debug("Records : %s", records)

    logger.info("Fetched %s cities, built %s records", len(cities), len(records))

    return records