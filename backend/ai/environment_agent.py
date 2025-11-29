import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AQI_API_KEY = os.getenv("AQI_API_KEY")

def get_environment_data(lat: float, lon: float) -> dict:
    """
    Fetches weather and air quality data for a given latitude and longitude.
    """
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        aqi_url = f"https://api.api-ninjas.com/v1/airquality?lat={lat}&lon={lon}"

        weather_res = requests.get(weather_url)
        aqi_res = requests.get(aqi_url, headers={"X-Api-Key": AQI_API_KEY})

        weather_res.raise_for_status()
        aqi_res.raise_for_status()

        weather_data = weather_res.json()
        aqi_data = aqi_res.json()

        return {
            "temperature": weather_data.get("main", {}).get("temp"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "description": weather_data.get("weather", [{}])[0].get("description"),
            "icon": weather_data.get("weather", [{}])[0].get("icon"),
            "city": weather_data.get("name"),
            "aqi": aqi_data.get("overall_aqi"),
            "pollutants": aqi_data
        }
    except requests.RequestException as e:
        raise Exception(f"API Request Error: {str(e)}")

def get_coordinates(city: str, country_code: str = None) -> list:
    """
    Fetches coordinates for a city using OpenWeatherMap Geocoding API.
    """
    try:
        query = f"{city},{country_code}" if country_code else city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={OPENWEATHER_API_KEY}"
        
        response = requests.get(geo_url)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            return []

        return [
            {
                "lat": loc["lat"],
                "lon": loc["lon"],
                "name": loc["name"],
                "country": loc["country"],
                "state": loc.get("state", "")
            }
            for loc in data
        ]
    except requests.RequestException:
        return []

def get_micro_aqi(lat: float, lon: float) -> list:
    """
    Simulates micro-zone AQI data (Traffic, Construction, etc.) around a location.
    In a real app, this would fetch from a granular API or IoT sensor network.
    """
    import random
    
    micro_zones = []
    types = [
        {"type": "Traffic Hotspot", "risk": "High", "offset": 0.005},
        {"type": "Construction Zone", "risk": "Severe", "offset": 0.003},
        {"type": "Industrial Belt", "risk": "High", "offset": 0.008},
        {"type": "Green Zone (Park)", "risk": "Low", "offset": 0.004},
        {"type": "Residential Area", "risk": "Moderate", "offset": 0.002},
        {"type": "Coastal Wind Zone", "risk": "Low", "offset": 0.006}
    ]

    # Generate 6-8 random points
    for _ in range(random.randint(6, 8)):
        zone = random.choice(types)
        # Randomize location slightly around the center
        p_lat = float(lat) + random.uniform(-zone["offset"], zone["offset"])
        p_lon = float(lon) + random.uniform(-zone["offset"], zone["offset"])
        
        # Simulate AQI based on type
        if zone["type"] == "Green Zone (Park)" or zone["type"] == "Coastal Wind Zone":
            aqi = random.randint(30, 80)
        elif zone["type"] == "Residential Area":
            aqi = random.randint(80, 150)
        else:
            aqi = random.randint(150, 350)

        micro_zones.append({
            "lat": p_lat,
            "lon": p_lon,
            "type": zone["type"],
            "aqi": aqi,
            "risk": zone["risk"]
        })
    
    return micro_zones

def get_aqi_forecast(lat: float, lon: float) -> list:
    """
    Fetches 12-hour AQI forecast using OpenWeatherMap Air Pollution API.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract next 12 hours (data is hourly)
        forecast = []
        for item in data.get('list', [])[:12]:
            # OpenWeatherMap AQI is 1-5 scale. We map it roughly to standard AQI for visualization
            # 1=Good(50), 2=Fair(100), 3=Moderate(150), 4=Poor(200), 5=Very Poor(300)
            owm_aqi = item['main']['aqi']
            aqi_map = {1: 40, 2: 80, 3: 120, 4: 180, 5: 250}
            
            forecast.append({
                "time": item['dt'], # Unix timestamp
                "aqi": aqi_map.get(owm_aqi, 100),
                "raw_aqi": owm_aqi
            })
            
        return forecast
    except requests.RequestException:
        return []
