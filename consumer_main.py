# consumer_main.py

from weather_platform.streaming import consume_records
from dotenv import load_dotenv
import logging
import os


load_dotenv()

level=os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def main():

    consume_records()


if __name__ == "__main__":
    main()