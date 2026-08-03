# main.py


import json
from pathlib import Path
import asyncio

from weather_platform.ingestion import fetch_many
from weather_platform.db import load_records
from weather_platform.config import get_connection
from dotenv import load_dotenv


load_dotenv()


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


def main():

    dicts_to_test = [{"country": "France", "city": "Paris", "latitude": 48.85, "longitude": 2.35}, {"country": "China", "city": "Shanghai", "latitude": 31.22, "longitude": 121.46},
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21},
                      {"country": "South Korea", "city": "Seoul", "latitude": 37.56, "longitude": 126.98}, {"country": "Canada", "city": "Toronto", "latitude": 43.66, "longitude": -79.39},
                      {"country": "Australia", "city": "Melbourne", "latitude": -37.81, "longitude": 144.97}, {"country": "Peru", "city": "Lima", "latitude": -12.05, "longitude": -77.03},
                      {"country": "United States", "city": "Miami", "latitude": 25.77, "longitude": -80.20}, {"country": "Russia", "city": "Moscow", "latitude": 55.76, "longitude": 37.62},
                      {"country": "Italia", "city": "Napoli", "latitude": 40.84, "longitude": 14.25}, {"country": "Nigeria", "city": "Lagos", "latitude": 6.50, "longitude": 3.34},
                      {"country": "India", "city": "Mumbai", "latitude": 18.949, "longitude": 72.84}, {"country": "Indonesia", "city": "Jakarta", "latitude": -6.22, "longitude": 106.85},
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Sweden", "city": "Stockholm", "latitude": 59.33, "longitude": 18.06}]
    
    jsondict = asyncio.run(fetch_many(dicts_to_test))
    # save_raw(jsondict, "data/testing/weather.json")

    load_records(jsondict)


    # connection_test()





if __name__ == "__main__":
    main()
