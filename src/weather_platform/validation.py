# src/weather_platform/validation.py

import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ['temperature_2m', 'wind_speed_10m', 'relative_humidity_2m', 'longitude', 'latitude', 'country', 'city', 'ingested_at', 'observed_at']

def is_valid_record(record: dict) -> bool:
    '''
    Helper function that checks if datas are valids.
    Args:
        record : dict of weather's data 
    Return:
        boolean 
    '''

    logger.debug('Checking if record : %s is valid...', record)

    for field in REQUIRED_FIELDS:

        if field not in record:

            logger.debug('Missing required field : %s', field)

            return False

    if record['temperature_2m'] < -90 or record['temperature_2m'] > 60:

        logger.debug('Temperature at 2m : %s is not valid!', record['temperature_2m'])

        return False

    if record['relative_humidity_2m'] < 0 or record['relative_humidity_2m'] > 100:

        logger.debug('relative_humidity_2m : %s is not in percent range!', record['relative_humidity_2m'])

        return False

    if record['wind_speed_10m'] < 0:

        logger.debug('wind_speed_10m : %s is not non negative!', record['wind_speed_10m'])

        return False

    logger.debug('Record datas validated!')

    return True