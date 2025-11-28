import requests
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from geopy import Nominatim
from dotenv import load_dotenv

load_dotenv(".env.weather")
weather_key = os.getenv("WEATHER_KEY")  # or os.environ["WEATHER_KEY"]

router = APIRouter()
geolocator = Nominatim(user_agent="my_fastapi_app")

# Allow either lat/lon or address input
class LocationInput(BaseModel):
    lat: float | None = None
    lon: float | None = None
    address: str | None = None

location_store = {}

@router.post("/location")
async def receive_location(data: LocationInput):
    lat, lon, address = data.lat, data.lon, data.address

    try:
        if address and not (lat and lon):
            # Forward geocoding: address -> coordinates
            location = geolocator.geocode(address, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
            else:
                raise HTTPException(status_code=404, detail="Address not found")
        elif lat is not None and lon is not None:
            # Reverse geocoding: coordinates -> address
            location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
            address = location.address if location else "Address not found"
        else:
            raise HTTPException(status_code=400, detail="Provide either lat/lon or address")
    except Exception as e:
        address = f"Error: {e}"

    # Store in memory
    location_store[(lat, lon)] = address

    # Call Google Weather API
    weather_url = (
        f"https://weather.googleapis.com/v1/forecast/hours:lookup?"
        f"key={weather_key}&location.latitude={lat}&location.longitude={lon}&hours=24"
    )
    try:
        weather_response = requests.get(weather_url)
        if weather_response.ok:
            weather_data = weather_response.json()
        else:
            weather_data = {"error": f"Weather API returned {weather_response.status_code}"}
    except Exception as e:
        weather_data = {"error": str(e)}

    return {
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "weather": weather_data
    }
