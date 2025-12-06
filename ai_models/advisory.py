import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Relevance AI Configuration
RELEVANCE_PROJECT = os.getenv("RELEVANCE_PROJECT")
RELEVANCE_API_KEY = os.getenv("RELEVANCE_API_KEY")
RELEVANCE_REGION = os.getenv("RELEVANCE_REGION", "d7b62b")
TOOL_ID = "92f0d1e5-c44d-41c5-a05a-ae75c58941a2"

def get_health_advice(env: dict) -> str:
    """
    Generates health advice based on environmental data using Relevance AI.
    """
    try:
        url = f"https://api-{RELEVANCE_REGION}.stack.tryrelevance.com/latest/studios/{TOOL_ID}/trigger"
        
        headers = {
            "Authorization": f"{RELEVANCE_PROJECT}:{RELEVANCE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Determine Risk Level for Context
        aqi = env.get('aqi', 0)
        risk_level = "Good"
        if aqi > 300: risk_level = "Hazardous"
        elif aqi > 200: risk_level = "Very Unhealthy"
        elif aqi > 150: risk_level = "Unhealthy"
        elif aqi > 100: risk_level = "Moderate"
        
        prompt = f"""
        **Environmental Data:**
        - AQI: {aqi} (Risk Level: {risk_level})
        - Temperature: {env.get('temperature')}°C
        - Humidity: {env.get('humidity')}%
        - Condition: {env.get('description')}
        
        **Pollutant Breakdown:**
        {env.get('pollutants')}

    **Task:**
    Provide a detailed, scientifically-backed daily health plan in markdown.
    
    **CRITICAL INSTRUCTION:**
    Your advice MUST be directly derived from the AQI of {aqi} ({risk_level}).
    - IF AQI > 150: You MUST strictly forbid outdoor strenuous exercise and recommend N95 masks.
    - IF AQI < 100: You MUST encourage ventilation and outdoor activities.
    - Do NOT provide generic advice that applies to all conditions. Tailor it specifically to {risk_level} air quality.

    **Required Output Format:**

    ### Executive Summary
    (One sentence summary)

    ### Key Risks
    (Bullet points of main risks)

    ### Morning Plan
    (Provide a comprehensive guide for the morning. Include:
    - **Activity**: Specific recommendations (exact times, types of exercise).
    - **Science**: Explain the "Why" with scientific depth (e.g., "PM2.5 levels are highest at dawn due to thermal inversion").
    - **Diet/Protection**: Specific dietary tips (e.g., antioxidants) or protective measures.
    - **Physiology**: How the body reacts to current pollutants.
    - **Actionable Steps**: Non-obvious tips.
    Aim for **5-6 detailed points**.)

    ### Afternoon Plan
    (Provide a comprehensive guide for the afternoon. Include:
    - **Work/School**: How to manage exposure during commute or work.
    - **Physiology**: Explain how hydration helps clear toxins.
    - **Actionable Steps**: Specific steps to improve indoor air quality.
    - **Mental Health**: Impact of pollution on focus and mood.
    Aim for **5-6 detailed points**.)

    ### Evening Plan
    (Provide a comprehensive guide for the evening. Include:
    - **Sleep Hygiene**: How pollution affects sleep and what to do.
    - **Ventilation**: Precise advice on when/if to open windows based on night-time pollution settling.
    - **Recovery**: Evening routines to help the lungs recover.
    - **Long-term**: Tips for long-term respiratory health.
    Aim for **5-6 detailed points**.)
    """
        
        payload = {
            "params": {
                "prompt": prompt
            },
            "project": RELEVANCE_PROJECT
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
            
        data = response.json()
        
        # Extract advice from the specific path
        advice = data.get("output", {}).get("transformed", {}).get("advice")
        
        if not advice:
             advice = data.get("output", {}).get("advice")
             
        if not advice:
            return f"Health advice unavailable (Parse Error). Raw: {str(data)}"
            
        return advice

    except Exception as e:
        return f"Health advice unavailable (Error: {str(e)}). Data: {env}"

# Import local data
try:
    from data.emergency_data import EMERGENCY_DATA, COUNTRY_DEFAULTS
except ImportError:
    EMERGENCY_DATA = {}
    COUNTRY_DEFAULTS = {}

def get_emergency_info(city: str, country: str) -> dict:
    """
    Fetches emergency contact numbers. Uses local data first, then Relevance AI.
    """
    # 1. Check Local City Data
    if city in EMERGENCY_DATA:
        return EMERGENCY_DATA[city]
        
    # 2. Check Local Country Data (if city not found)
    # We need the country code (e.g., 'AU') but 'country' arg might be 'Australia' or 'AU'
    # The frontend sends 'AU' (cca2 code).
    if country in COUNTRY_DEFAULTS:
        return COUNTRY_DEFAULTS[country]

    try:
        url = f"https://api-{RELEVANCE_REGION}.stack.tryrelevance.com/latest/studios/{TOOL_ID}/trigger"
        
        headers = {
            "Authorization": f"{RELEVANCE_PROJECT}:{RELEVANCE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        **Task:**
        Provide the emergency contact numbers for **{city}, {country}**.
        
        **Required Output Format (JSON):**
        {{
            "ambulance": "Phone Number",
            "police": "Phone Number",
            "general": "Phone Number (e.g. 911, 112)",
            "notes": "Brief 1-sentence advice specific to this location."
        }}
        
        **Constraints:**
        - Return ONLY valid JSON.
        - If specific city numbers aren't found, use National numbers for {country}.
        """
        
        payload = {
            "params": {
                "prompt": prompt
            },
            "project": RELEVANCE_PROJECT
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        output = data.get("output", {}).get("transformed", {}).get("advice")
        
        if not output:
             output = data.get("output", {}).get("advice")

        # Clean up code blocks if present
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0]
        elif "```" in output:
            output = output.split("```")[1].split("```")[0]
            
        import json
        return json.loads(output.strip())

    except Exception as e:
        print(f"Emergency info error: {e}")
        return {
            "ambulance": "112", 
            "police": "112", 
            "general": "112", 
            "notes": "Could not fetch local numbers. Dial 112 for international emergency."
        }
