import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AQI_API_KEY = os.getenv("AQI_API_KEY")

def get_environment_data(lat, lon):
    
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    aqi_url = (
        f"https://api.api-ninjas.com/v1/airquality?"
        f"lat={lat}&lon={lon}"
    )

    weather = requests.get(weather_url).json()
    aqi = requests.get(aqi_url, headers={"X-Api-Key": AQI_API_KEY}).json()
    
    data = {
        "temperature": weather.get("main", {}).get("temp"),
        "humidity": weather.get("main", {}).get("humidity"),
        "description": weather.get("weather", [{}])[0].get("description"),
        "icon": weather.get("weather", [{}])[0].get("icon"),
        "aqi": aqi.get("overall_aqi"),
        "pollutants": aqi 
    }

    return data

def get_coordinates(city, country_code=None):
    """
    Get coordinates for a city using OpenWeatherMap Geocoding API.
    """
    query = f"{city},{country_code}" if country_code else city
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={OPENWEATHER_API_KEY}"
    
    response = requests.get(geo_url)
    if response.status_code == 200 and response.json():
        return [
            {
                "lat": loc["lat"],
                "lon": loc["lon"],
                "name": loc["name"],
                "country": loc["country"],
                "state": loc.get("state", "")
            }
            for loc in response.json()
        ]
    return []
