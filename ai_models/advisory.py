import requests
import json
import os

# User's Gemini API Key
GEMINI_API_KEY = "AIzaSyD3X291LCTYJZKt3-bgDXKH-mGTp7afgFo"

def get_health_advice(env: dict) -> dict:
    """
    Generates comprehensive health analysis and daily plans using Google Gemini 1.5 Flash.
    Returns a dictionary with 'assessment', 'morning_plan', 'afternoon_plan', 'evening_plan'.
    """
    # API URL for Google Gemini (AI Model)
    try:
        # We use 'gemini-1.5-flash' because it is faster and more stable than 'gemini-flash-latest'.
        # If you see a 503 error, it means the model is overloaded or down.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # Headers tell the server we are sending JSON data
        headers = {
            "Content-Type": "application/json"
        }
        
        # Determine Risk Level Logic (Synced with UI)
        aqi = env.get('aqi', 0)
        risk_level = "Good"
        if aqi > 150: risk_level = "Hazardous"
        elif aqi > 100: risk_level = "Unhealthy"
        elif aqi > 50: risk_level = "Moderate"
        else: risk_level = "Good"
        
        prompt = f"""
        **Context:**
        You are an expert environmental health scientist acting as a personal advisor.
        
        **Real-Time Data:**
        - AQI: {aqi} (Status: {risk_level})
        - Location: {env.get('city', 'Unknown')}
        - Temperature: {env.get('temperature')}°C
        - Humidity: {env.get('humidity')}%
        - Pollutants: {env.get('pollutants')}
        
        **CRITICAL CONSTRAINTS:**
        1. **CONSISTENCY**: You MUST accept the AQI is {aqi} ({risk_level}). Do NOT re-calculate or hallcinate a different AQI class.
        2. **DEPTH**: Provide scientifically rigorous analysis (e.g., mention specific physiological effects of PM2.5/NO2).
        3. **FORMAT**: Return ONLY valid JSON.
        
        **JSON Structure Required:**
        {{
            "assessment": "A deep, 3-paragraph scientific analysis of the current air quality. Use markdown. Mention specific risks to respiratory/cardiovascular systems. NO generic advice.",
            "morning_plan": "Specific, actionable advice for the Morning (e.g. 6AM-12PM). Mention exercise feasibility.",
            "afternoon_plan": "Specific advice for Afternoon (e.g. 12PM-5PM). Focus on work/school/protection.",
            "evening_plan": "Specific advice for Evening (e.g. 5PM-Sleep). Focus on sleep hygiene/ventilation.",
            "sources": ["List", "of", "likely", "pollutant", "sources", "based", "on", "location/context"],
            "source_narrative": "A 2-sentence explanation of WHY pollution is high (e.g. 'Stagnant winds trapping emissions...')."
        }}
        """
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        
        # Parse JSON
        result = json.loads(text_response)
        
        # Post-process: Ensure consistency if AI slipped up (though JSON mode usually fix it)
        # We will prepend the standard header to the 'assessment' part
        header = f"### Current Status: AQI {aqi} ({risk_level})\n"
        if "assessment" in result:
             # Remove self-references to AQI to avoid conflict, relying on our header
             import re
             clean_assessment = re.sub(r'AQI\s*:?\s*\d+', '', result["assessment"], flags=re.IGNORECASE)
             result["assessment"] = header + clean_assessment
             
        return result

    except Exception as e:
        print(f"Gemini Error: {e}")
        # Fallback to local planner if API fails
        # Use structured local data so cards are NOT empty
        from .planner import _get_comprehensive_data
        fallback_data = _get_comprehensive_data(env)
        return {
            "assessment": fallback_data["assessment"],
            "morning_plan": fallback_data["morning"],
            "afternoon_plan": fallback_data["afternoon"],
            "evening_plan": fallback_data["evening"]
        }

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
