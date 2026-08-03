# tests/test_validation.py

from datetime import datetime, timezone

from weather_platform.validation import is_valid_record


base_record = {
    "ingested_at": datetime.now(timezone.utc).isoformat(),
    "country": "France",
    "city": "Metz",
    "latitude": 49.12,
    "longitude": 6.17,
    "observed_at": datetime(2026, 6, 8, 17, 0).isoformat(),
    "temperature_2m": 20.4,
    "relative_humidity_2m": 72,
    "wind_speed_10m": 11.7
}


def test_valid_record_passes():
    """
    Test function to see if it record correctly when the record is valid.
    """

    record = {**base_record}

    assert is_valid_record(record)


def test_temperature_too_high_too_low_fails():
    """
    Test function to see if a record with a very high or low temperature is invalidated.
    """

    record = {**base_record, "temperature_2m": 5000}
    record_2 = {**base_record, "temperature_2m": -5000}
    
    assert not is_valid_record(record)
    assert not is_valid_record(record_2)


def test_humidity_too_high_too_low_fails():
    """
    Test function to see if a record with a very high or low relative humidity is invalidated.
    """

    record = {**base_record, "relative_humidity_2m": 172}
    record_2 = {**base_record, "relative_humidity_2m": -72}
    
    assert not is_valid_record(record)
    assert not is_valid_record(record_2)


def test_wind_speed_negative_fails():
    """
    Test function to see if a record with a negative wind speed is invalidated.
    """

    record = {**base_record, "wind_speed_10m": -10}
    
    assert not is_valid_record(record)


def test_missing_field_fails():
    """
    Test function to see if a record is missing
    """

    record = {k: v for k, v in base_record.items() if k != "city"}

    assert not is_valid_record(record)