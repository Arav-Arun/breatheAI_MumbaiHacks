import requests
import json
import os

# User's Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_health_advice(env: dict) -> dict:
    """
    Generates comprehensive health analysis and daily plans using Google Gemini 1.5 Flash.
    Returns a dictionary with 'assessment', 'morning_plan', 'afternoon_plan', 'evening_plan'.
    """
    # API URL for Google Gemini (AI Model)
    try:
        # We use 'gemini-flash-latest' as it is the currently verified working model alias.
        # 'gemini-1.5-flash' returned 404.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
        
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
        
        location_context = f"{env.get('city', 'Unknown')}, {env.get('state', '')} {env.get('country', '')}".strip()

        prompt = f"""
        **Context:**
        You are an expert environmental health scientist acting as a personal advisor for a user in **{location_context}**.
        
        **Real-Time Data:**
        - AQI: {aqi} (Status: {risk_level})
        - Location: {location_context}
        - Temperature: {env.get('temperature')}°C
        - Humidity: {env.get('humidity')}%
        - Pollutants: {env.get('pollutants')}
        
        **CRITICAL CONSTRAINTS:**
        1. **CONSISTENCY**: You MUST accept the AQI is {aqi} ({risk_level}).
        2. **TONE**: Professional, empathetic, and concise. Avoid alarmist language but be firm.
        3. **FORMAT**: Return ONLY valid JSON.
        4. **NO REPETITION**: The user already sees the AQI number and "Hazardous/Good" status in the header.
        5. **LOCAL SPECIFICITY**: Use the location ({location_context}) to infer specific pollution sources (e.g. if hill station: "Forest fires/Tourism/Solid waste"; if city: "Traffic/Industrial"). Tailor advice to the specific geography (e.g. "Avoid valley floor" vs "Avoid main roads").
        
        **JSON Structure Required:**
        {{
            "assessment": "A deep, 3-paragraph scientific analysis... Mention specific risks... Focus on the specific location context.",
            "morning_plan": "Specific, actionable advice for the Morning...",
            "afternoon_plan": "Specific advice for Afternoon...",
            "evening_plan": "Specific advice for Evening...",
            "sources": ["List", "of", "likely", "pollutant", "sources", "based", "on", "{location_context}"],
            "source_narrative": "A 2-sentence explanation of WHY pollution is high in {location_context} (e.g. 'Inversions in the valley...')."
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
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return _get_fallback_advice(risk_level)
            
        result_json = response.json()
        try:
            # Extract text
            text_content = result_json['candidates'][0]['content']['parts'][0]['text']
            # Clean comments like ```json ... ```
            clean_text = text_content.replace('```json', '').replace('```', '').strip()
            
            parsed_data = json.loads(clean_text)
            
            # Helper to safely add header
            header = f"### Current Status: AQI {aqi} ({risk_level})\n"
            if "assessment" in parsed_data:
                 parsed_data["assessment"] = header + parsed_data["assessment"]
            
            return parsed_data
            
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            return _get_fallback_advice(risk_level)

    except Exception as e:
        return _get_fallback_advice(env)

def _get_fallback_advice(env: dict) -> dict:
    """Fallback if AI fails."""
    # Use structured local data so cards are NOT empty
    from .planner import _get_comprehensive_data
    fallback_data = _get_comprehensive_data(env)
    return {
        "assessment": fallback_data["assessment"],
        "morning_plan": fallback_data["morning"],
        "afternoon_plan": fallback_data["afternoon"],
        "evening_plan": fallback_data["evening"],
        "sources": ["Data Unavailable", "Check Internet"],
        "source_narrative": "Unable to analyze sources at this time due to AI service disruption."
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
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
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
