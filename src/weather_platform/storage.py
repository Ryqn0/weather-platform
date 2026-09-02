# src/weather_platform/storage.py

import json
import logging

from google.cloud import storage


logger = logging.getLogger(__name__)


def save_raw_to_gcs(data: list[dict], bucket_name: str, object_path: str) -> None:
    """Upload the raw API responses as JSON to a GCS object."""

    logger.debug("Creating storage client Object using google cloud API...")
    storage_client = storage.Client()

    logger.debug("Getting bucket with bucket name: %s", bucket_name)
    bucket = storage_client.bucket(bucket_name)

    logger.debug("Getting blob with object path: %s", object_path)
    blob = bucket.blob(object_path)

    logger.debug("Uploading data as json: %s", data)
    blob.upload_from_string(json.dumps(data), content_type="application/json")

    logger.debug("Data uploaded successfully!")