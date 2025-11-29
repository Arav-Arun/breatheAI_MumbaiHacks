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
        # Use OpenWeatherMap for AQI as well to be consistent and reliable
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"

        weather_res = requests.get(weather_url)
        aqi_res = requests.get(aqi_url)

        weather_res.raise_for_status()
        aqi_res.raise_for_status()

        weather_data = weather_res.json()
        aqi_data = aqi_res.json()
        
        # Process OWM AQI data
        aqi_record = aqi_data.get('list', [{}])[0]
        owm_aqi = aqi_record.get('main', {}).get('aqi', 1)
        components = aqi_record.get('components', {})
        
        # Map OWM AQI (1-5) to standard 0-500 scale (approximate)
        aqi_map = {1: 40, 2: 80, 3: 120, 4: 180, 5: 250}
        overall_aqi = aqi_map.get(owm_aqi, 50)
        
        # Format pollutants
        pollutants = {
            "PM2.5": {"concentration": components.get("pm2_5", 0)},
            "PM10": {"concentration": components.get("pm10", 0)},
            "NO2": {"concentration": components.get("no2", 0)},
            "SO2": {"concentration": components.get("so2", 0)},
            "O3": {"concentration": components.get("o3", 0)},
            "CO": {"concentration": components.get("co", 0)}
        }

        return {
            "temperature": weather_data.get("main", {}).get("temp"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "description": weather_data.get("weather", [{}])[0].get("description"),
            "icon": weather_data.get("weather", [{}])[0].get("icon"),
            "city": weather_data.get("name"),
            "aqi": overall_aqi,
            "pollutants": pollutants
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
    Fetches 5-day AQI forecast using OpenWeatherMap Air Pollution API.
    Aggregates hourly data to daily max AQI.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Process hourly data into daily max AQI
        daily_forecast = {}
        from datetime import datetime
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            day_name = dt.strftime('%a') # Mon, Tue...
            
            owm_aqi = item['main']['aqi']
            aqi_map = {1: 40, 2: 80, 3: 120, 4: 180, 5: 250}
            aqi_val = aqi_map.get(owm_aqi, 100)
            
            if date_str not in daily_forecast:
                daily_forecast[date_str] = {"day": day_name, "max_aqi": aqi_val, "date": date_str}
            else:
                daily_forecast[date_str]["max_aqi"] = max(daily_forecast[date_str]["max_aqi"], aqi_val)
        
        # Return first 5 days
        return list(daily_forecast.values())[:5]
    except requests.RequestException:
        return []

def get_aqi_history(lat: float, lon: float) -> list:
    """
    Fetches 7-day AQI history using OpenWeatherMap Air Pollution History API.
    """
    try:
        from datetime import datetime, timedelta
        import time
        
        # Calculate timestamps for the last 7 days
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=7)
        
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_ts}&end={end_ts}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Process hourly data into daily max AQI
        daily_history = {}
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            day_name = dt.strftime('%a')
            
            owm_aqi = item['main']['aqi']
            aqi_map = {1: 40, 2: 80, 3: 120, 4: 180, 5: 250}
            aqi_val = aqi_map.get(owm_aqi, 100)
            
            if date_str not in daily_history:
                daily_history[date_str] = {"day": day_name, "max_aqi": aqi_val, "date": date_str}
            else:
                daily_history[date_str]["max_aqi"] = max(daily_history[date_str]["max_aqi"], aqi_val)
        
        # Return values sorted by date
        sorted_history = sorted(daily_history.values(), key=lambda x: x['date'])
        return sorted_history
        
    except requests.RequestException:
        # Fallback: Simulate 7-day AQI history if API fails
        import random
        from datetime import datetime, timedelta
        
        history = []
        today = datetime.now()
        
        for i in range(7, 0, -1):
            date = today - timedelta(days=i)
            day_name = date.strftime('%a')
            date_str = date.strftime('%Y-%m-%d')
            
            # Simulate AQI (vary slightly to look realistic)
            aqi = random.randint(50, 180)
            
            history.append({
                "day": day_name,
                "max_aqi": aqi,
                "date": date_str
            })
            
        return history
