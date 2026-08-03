import asyncio, time, httpx
from datetime import datetime, timezone
from weather_platform.ingestion import fetch_many   # your concurrent version
# paste your city list here (or import it)
cities = [{"country": "France", "city": "Paris", "latitude": 48.85, "longitude": 2.35}, {"country": "China", "city": "Shanghai", "latitude": 31.22, "longitude": 121.46},
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Brazil", "city": "Rio de Janeiro", "latitude": -22.90, "longitude": -43.21},
                      {"country": "South Korea", "city": "Seoul", "latitude": 37.56, "longitude": 126.98}, {"country": "Canada", "city": "Toronto", "latitude": 43.66, "longitude": -79.39},
                      {"country": "Australia", "city": "Melbourne", "latitude": -37.81, "longitude": 144.97}, {"country": "Peru", "city": "Lima", "latitude": -12.05, "longitude": -77.03},
                      {"country": "United States", "city": "Miami", "latitude": 25.77, "longitude": -80.20}, {"country": "Russia", "city": "Moscow", "latitude": 55.76, "longitude": 37.62},
                      {"country": "Italia", "city": "Napoli", "latitude": 40.84, "longitude": 14.25}, {"country": "Nigeria", "city": "Lagos", "latitude": 6.50, "longitude": 3.34},
                      {"country": "India", "city": "Mumbai", "latitude": 18.949, "longitude": 72.84}, {"country": "Indonesia", "city": "Jakarta", "latitude": -6.22, "longitude": 106.85},
                      {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.69, "longitude": 46.72}, {"country": "Sweden", "city": "Stockholm", "latitude": 59.33, "longitude": 18.06}] * \
                        6
    

# --- sequential baseline: one request at a time, awaited in a plain loop ---
async def fetch_sequential(cities):
    async with httpx.AsyncClient() as client:
        results = []
        for c in cities:
            r = await client.get("https://api.open-meteo.com/v1/forecast",
                                  params={"latitude": c["latitude"], "longitude": c["longitude"],
                                          "current": ["temperature_2m"]}, timeout=10)
            results.append(r.json())
    return results

# time sequential
start = time.perf_counter()
asyncio.run(fetch_sequential(cities))
print(f"Sequential: {time.perf_counter() - start:.2f}s")

# time concurrent
start = time.perf_counter()
asyncio.run(fetch_many(cities))
print(f"Concurrent: {time.perf_counter() - start:.2f}s")