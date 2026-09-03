# src/weather_platform/streaming.py

import os
from confluent_kafka import Producer, Consumer
from weather_platform.db import load_records
from dotenv import load_dotenv
import logging
import json

logger = logging.getLogger(__name__)

load_dotenv()

def delivery_report(err, msg):

    if err is not None:

        logger.warning("Failed to deliver message: %s: %s", str(msg), str(err))

    else:

        logger.debug("Message produced: %s", str(msg))


def publish_records(records: list[dict], topic: str = "weather-readings") -> None:
    """Publish each weather record to Kafka, keyed by city."""

    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS")})

    logger.info("Publishing records...")

    for record in records:

        producer.produce(topic, key=record['city'], value=json.dumps(record).encode("utf-8"), callback=delivery_report)

    producer.flush()        

    logger.info("Finished to treat the %s records", len(records))


def consume_records(topic: str = "weather-readings", group_id: str = "weather-loader") -> None:
    """Consume weather records from Kafka forever, loading each to Postgres."""

    consumer = Consumer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
                         "group.id": group_id,
                         "auto.offset.reset": "earliest",
                        })

    try:

        logger.info("Consuming records...")

        consumer.subscribe([topic])

        running = True

        while running:

            msg = consumer.poll(timeout=1.0)

            if msg is None: continue

            if msg.error():

                logger.warning("ERROR: %s", msg.error())

            else:

                try:

                    record = json.loads(msg.value())

                    logger.debug("Loading record : %s into the database", record)

                    load_records([record])

                    logger.debug("Loaded record!")

                except json.JSONDecodeError:

                    logger.warning("Skipping malformed message at offset %s", msg.offset())

                    continue

    finally:

        consumer.close()

        logger.info("Consumer closed!")


def consume_alerts(topic: str = "weather-readings", group_id: str = "weather-alerts") -> None:
    """Consume readings and log warnings for extreme temperatures."""

    consumer = Consumer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
                         "group.id": group_id,
                         "auto.offset.reset": "earliest",
                        })

    THRESHOLD_1 = -10
    THRESHOLD_2 = 35

    try:

        logger.info("Consuming alerts...")

        consumer.subscribe([topic])

        running = True

        while running:

            msg = consumer.poll(timeout=1.0)

            if msg is None: continue

            if msg.error():

                logger.warning("ERROR: %s", msg.error())

            else:

                try:

                    record = json.loads(msg.value())
                    city = record["city"]
                    temp = record["temperature_2m"]

                    logger.info("Checking temperature : %s if it is between thresholds %s and %s ", temp, THRESHOLD_1, THRESHOLD_2)

                    if temp < THRESHOLD_1:

                        logger.warning("Extreme cold in %s: %s°C (threshold %s)", city, temp, THRESHOLD_1)

                    elif temp > THRESHOLD_2:

                        logger.warning("Extreme heat in %s: %s°C (threshold %s)", city, temp, THRESHOLD_2)

                    else:

                        logger.info("Temperature (%s) in %s is normal)", city, temp)

                    logger.info("Temperature check successfull!")

                except (json.JSONDecodeError, KeyError):

                    logger.warning("Skipping malformed message at offset %s", msg.offset())

                    continue


    finally:

        consumer.close()

        logger.info("Consumer closed!")