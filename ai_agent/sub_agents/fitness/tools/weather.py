import requests

def get_location(lat: float, lon: float) -> dict:
    """
    Get location and weather information for given coordinates by calling a FastAPI endpoint.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: A dictionary containing location details and weather info (if provided by the endpoint),
              or an 'error' key if the request fails.
    """
    endpoint = "http://127.0.0.1:8000/location"  # FastAPI endpoint
    payload = {"lat": lat, "lon": lon}

    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        return {"error": str(e)}
