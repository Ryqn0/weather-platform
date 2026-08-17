# tests/test_ingestion.py

import httpx, respx, asyncio, pytest
from weather_platform.ingestion import fetch_current_weather


@respx.mock
async def test_fetch_returns_parsed_json():
    """
    Test a normal response with http status 200
    """

    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json={"current": {"time": "2026-08-03T13:00", "temperature_2m": 20.4, "relative_humidity_2m": 72, "wind_speed_10m": 11.7}})
    )
    
    async with httpx.AsyncClient() as client:

        result = await fetch_current_weather(client, asyncio.Semaphore(1), 49.12, 6.17)

    
    assert result["current"]["temperature_2m"] == 20.4



@respx.mock
async def test_fetch_returns_error_json():
    """
    Test an error response
    """

    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(429, json={"error_status": "HTTP Error 429 : Too many requests"})
    )
    
    async with httpx.AsyncClient() as client:

        result = await fetch_current_weather(client, asyncio.Semaphore(1), 49.12, 6.17)

    
    assert "error_status" in result



@respx.mock
async def test_fetch_returns_connection_error():
    """
    Test a network error path
    """

    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        side_effect=httpx.ConnectError("boom")
    )
    
    async with httpx.AsyncClient() as client:

        result = await fetch_current_weather(client, asyncio.Semaphore(1), 49.12, 6.17)

    
    assert "error_status" in result