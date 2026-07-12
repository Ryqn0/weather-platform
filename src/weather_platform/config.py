# src/weather-platform/config.py

from dotenv import load_dotenv
import psycopg
import os

load_dotenv()

def get_connection():

    return psycopg.connect(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"))