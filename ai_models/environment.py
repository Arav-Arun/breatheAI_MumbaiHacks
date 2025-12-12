import os
import requests
import math
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AQI_API_KEY = os.getenv("AQI_API_KEY")

def calculate_aqi(pm25: float) -> int:
    """
    Calculates AQI based on PM2.5 concentration using US EPA standards.
    """
    c = round(pm25, 1)
    
    if c <= 12.0:
        return int(round(((50 - 0) / (12.0 - 0)) * (c - 0) + 0))
    elif c <= 35.4:
        return int(round(((100 - 51) / (35.4 - 12.1)) * (c - 12.1) + 51))
    elif c <= 55.4:
        return int(round(((150 - 101) / (55.4 - 35.5)) * (c - 35.5) + 101))
    elif c <= 150.4:
        return int(round(((200 - 151) / (150.4 - 55.5)) * (c - 55.5) + 151))
    elif c <= 250.4:
        return int(round(((300 - 201) / (250.4 - 150.5)) * (c - 150.5) + 201))
    elif c <= 350.4:
        return int(round(((400 - 301) / (350.4 - 250.5)) * (c - 250.5) + 301))
    elif c <= 500.4:
        return int(round(((500 - 401) / (500.4 - 350.5)) * (c - 350.5) + 401))
    else:
        return 500

def calculate_cigarettes(pm25: float) -> float:
    """
    Calculates cigarette equivalent based on Berkeley Earth rule of thumb.
    1 cigarette approx 22 ug/m3 of PM2.5 per day.
    """
    if pm25 <= 0: return 0.0
    return round(pm25 / 22.0, 1)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two points in km."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_waqi_data(lat: float, lon: float) -> dict:
    """Fetches AQI data from WAQI API with 25km distance check."""
    try:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'ok':
            return {}
            
        result = data.get('data', {})
        
        # Distance Check meant to avoid distant city data for rural areas
        station_geo = result.get('city', {}).get('geo', [])
        if len(station_geo) >= 2:
            try:
                station_lat, station_lon = float(station_geo[0]), float(station_geo[1])
                dist = haversine_distance(lat, lon, station_lat, station_lon)
                print(f"WAQI Station Distance: {dist:.1f} km ({result.get('city', {}).get('name')})")
                
                if dist > 25:
                    print("WAQI Station too far (>25km). Fallback to OWM.")
                    return {}
            except Exception as e:
                print(f"Distance calc error: {e}")

        return result
    except Exception as e:
        print(f"WAQI API Error: {e}")
        return {}

def get_owm_pollution(lat: float, lon: float) -> dict:
    """Fetches pollution data from OpenWeatherMap as fallback."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('list'):
            return {}
            
        record = data['list'][0]
        components = record.get('components', {})
        pm25 = components.get('pm2_5', 0)
        
        return {
            "aqi": calculate_aqi(pm25),
            "pollutants": {
                "PM2.5": {"concentration": components.get("pm2_5", 0)},
                "PM10": {"concentration": components.get("pm10", 0)},
                "NO2": {"concentration": components.get("no2", 0)},
                "SO2": {"concentration": components.get("so2", 0)},
                "O3": {"concentration": components.get("o3", 0)},
                "CO": {"concentration": components.get("co", 0)}
            }
        }
    except Exception as e:
        print(f"OWM Pollution Error: {e}")
        return {}


def get_environment_data(lat: float, lon: float, override_city: str = None) -> dict:
    """Fetches weather and air quality data."""
    try:
        # 1. Weather Data (OpenWeatherMap)
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        weather_res = requests.get(weather_url, timeout=5)
        weather_res.raise_for_status()
        weather_data = weather_res.json()
        
        # 2. AQI Data (Try WAQI first, then OWM)
        aqi_data = {}
        waqi_data = get_waqi_data(lat, lon)
        
        if waqi_data:
            # Process WAQI Data
            iaqi = waqi_data.get('iaqi', {})
            aqi_data = {
                "aqi": waqi_data.get('aqi', 0),
                "pollutants": {
                    "PM2.5": {"concentration": iaqi.get("pm25", {}).get("v", 0)},
                    "PM10": {"concentration": iaqi.get("pm10", {}).get("v", 0)},
                    "NO2": {"concentration": iaqi.get("no2", {}).get("v", 0)},
                    "SO2": {"concentration": iaqi.get("so2", {}).get("v", 0)},
                    "O3": {"concentration": iaqi.get("o3", {}).get("v", 0)},
                    "CO": {"concentration": iaqi.get("co", {}).get("v", 0)}
                }
            }
        else:
            # Fallback to OWM
            print("WAQI failed, falling back to OWM...")
            aqi_data = get_owm_pollution(lat, lon)

        # Default if both fail
        if not aqi_data:
            aqi_data = {
                "aqi": 0,
                "pollutants": {k: {"concentration": 0} for k in ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"]}
            }

        # Determine City Name
        # Priority: Override > OWM (Weather Name) > WAQI (Station Name)
        city_name = override_city
        if not city_name:
             city_name = weather_data.get("name", waqi_data.get('city', {}).get('name'))

        return {
            "temperature": weather_data.get("main", {}).get("temp"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "description": weather_data.get("weather", [{}])[0].get("description"),
            "icon": weather_data.get("weather", [{}])[0].get("icon"),
            "city": city_name, 
            "country": weather_data.get("sys", {}).get("country"),
            "aqi": aqi_data['aqi'],
            "pollutants": aqi_data['pollutants'],
            "lat": lat,
            "lon": lon
        }
    except requests.RequestException as e:
        raise Exception(f"API Request Error: {str(e)}")

def get_coordinates(city: str, country_code: str = None) -> list:
    """Fetches coordinates for a city."""
    try:
        query = f"{city},{country_code}" if country_code else city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={OPENWEATHER_API_KEY}"
        
        response = requests.get(geo_url, timeout=5)
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



def get_aqi_forecast(lat: float, lon: float) -> list:
    """Fetches 5-day AQI forecast."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        daily_forecast = {}
        from datetime import datetime
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            day_name = dt.strftime('%a')
            
            pm25 = item['components']['pm2_5']
            aqi_val = calculate_aqi(pm25)
            
            if date_str not in daily_forecast:
                daily_forecast[date_str] = {"day": day_name, "max_aqi": aqi_val, "date": date_str}
            else:
                daily_forecast[date_str]["max_aqi"] = max(daily_forecast[date_str]["max_aqi"], aqi_val)
        
        return list(daily_forecast.values())[:5]
    except requests.RequestException:
        return []

def get_aqi_history(lat: float, lon: float) -> list:
    """Fetches 7-day AQI history."""
    try:
        from datetime import datetime, timedelta
        
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=7)
        
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_ts}&end={end_ts}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        daily_history = {}
        
        for item in data.get('list', []):
            dt = datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            day_name = dt.strftime('%a')
            
            pm25 = item['components']['pm2_5']
            aqi_val = calculate_aqi(pm25)
            
            if date_str not in daily_history:
                daily_history[date_str] = {"day": day_name, "max_aqi": aqi_val, "date": date_str}
            else:
                daily_history[date_str]["max_aqi"] = max(daily_history[date_str]["max_aqi"], aqi_val)
        
        sorted_history = sorted(daily_history.values(), key=lambda x: x['date'])
        return sorted_history
        
    except requests.RequestException:
        return []
