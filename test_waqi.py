import os
import requests
from dotenv import load_dotenv

load_dotenv()

AQI_API_KEY = os.getenv("AQI_API_KEY")
print(f"API Key present: {bool(AQI_API_KEY)}")

# Test with a known location (e.g., London)
lat = 51.5074
lon = -0.1278

url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_API_KEY}"
print(f"Requesting: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response Status: {data.get('status')}")
    if data.get('status') == 'ok':
        print("Data keys:", data.get('data', {}).keys())
        print("IAQI keys:", data.get('data', {}).get('iaqi', {}).keys())
        print("AQI:", data.get('data', {}).get('aqi'))
    else:
        print("Error Message:", data.get('data'))
except Exception as e:
    print(f"Error: {e}")
