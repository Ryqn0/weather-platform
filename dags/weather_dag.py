# dags/weather_dag.py

from airflow.sdk import dag, task
from datetime import datetime

from weather_platform.ingestion import fetch_many
from weather_platform.db import load_records


@dag(
    default_args={
        "retries": 2,
    },
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
)


def ingest_pipeline():
    """
    Pipeline to test Airflow 
    """
    
    cities = [{"country": "France", "city": "Paris", "latitude": 48.85, "longitude": 2.35}, {"country": "China", "city": "Shanghai", "latitude": 31.22, "longitude": 121.46},
              {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21}]


    @task()
    def fetch() -> list[dict]:
        """
        Call fetch_many fucntion
        """
        return fetch_many(cities)
    

    @task()
    def load(records: list[dict]):
        """
        Load the data into datasets
        """
        load_records(records)
        

    load(fetch())


ingest_pipeline()