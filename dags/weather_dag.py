# dags/weather_dag.py

from airflow.sdk import dag, task
from datetime import datetime

from weather_platform.ingestion import fetch_many
from weather_platform.db import load_records
from weather_platform.streaming import publish_records
import asyncio, time
import logging
from dotenv import load_dotenv

from airflow.providers.standard.operators.bash import BashOperator


load_dotenv()

# logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s')

logger = logging.getLogger(__name__)


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
              {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21},
              {"country": "South Korea", "city": "Seoul", "latitude": 37.56, "longitude": 126.98}, {"country": "Canada", "city": "Toronto", "latitude": 43.66, "longitude": -79.39},
              {"country": "Australia", "city": "Melbourne", "latitude": -37.81, "longitude": 144.97}, {"country": "Peru", "city": "Lima", "latitude": -12.05, "longitude": -77.03},
              {"country": "United States", "city": "Miami", "latitude": 25.77, "longitude": -80.20}, {"country": "Russia", "city": "Moscow", "latitude": 55.76, "longitude": 37.62},
              {"country": "Italia", "city": "Napoli", "latitude": 40.84, "longitude": 14.25}, {"country": "Nigeria", "city": "Lagos", "latitude": 6.50, "longitude": 3.34},
              {"country": "India", "city": "Mumbai", "latitude": 18.949, "longitude": 72.84}, {"country": "Indonesia", "city": "Jakarta", "latitude": -6.22, "longitude": 106.85},
              {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Sweden", "city": "Stockholm", "latitude": 59.33, "longitude": 18.06}]

    # {"country": "Nowhere", "city": "FakeCity", "latitude": 999, "longitude": 999} to debug

    @task()
    def fetch() -> list[dict]:
        """
        Call fetch_many fucntion
        """
        return asyncio.run(fetch_many(cities))
    

    # @task()
    # def load(records: list[dict]):
    #     """
    #     Load the data into datasets
    #     """
    #     load_records(records)


    @task
    def publish(records: list[dict]):
        """
        Publish the records
        """
        publish_records(records, "weather-readings")


    transform = BashOperator(
        task_id="transform",
        bash_command="cd /opt/airflow/weather_dbt && dbt deps && dbt run && dbt test",
    )

    # start = time.perf_counter()

    records = fetch()

    # transform.set_upstream(load(records))

    transform.set_upstream(publish(records))

    #print(f"Time taken to process : {time.perf_counter() - start:.2f}s")


ingest_pipeline()