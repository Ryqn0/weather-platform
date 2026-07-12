# main.py

import requests
import json
from pathlib import Path
from datetime import datetime, timezone
import psycopg
from dotenv import load_dotenv
import os

from weather_platform.ingestion import fetch_many
from weather_platform.db import load_records
from weather_platform.config import get_connection


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
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21}]
    
    jsondict = fetch_many(dicts_to_test)
    # save_raw(jsondict, "data/testing/weather.json")

    load_records(jsondict)


    # connection_test()





if __name__ == "__main__":
    main()
