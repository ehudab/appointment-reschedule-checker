import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("API_KEY")
def get_weather_full(lat, lon, api_key=api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric" 
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Returns the full JSON response dictionary
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}

if __name__ == "__main__":
    # Example usage
    lat = 37.7749  # Latitude for San Francisco
    lon = -122.4194  # Longitude for San Francisco

    print(get_weather_full(lat, lon))