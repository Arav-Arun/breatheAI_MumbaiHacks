
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Relevance AI Configuration
RELEVANCE_PROJECT = os.getenv("RELEVANCE_PROJECT", "c4a02a8b-ff68-4daf-b1ea-903e18fefb4f")
RELEVANCE_API_KEY = os.getenv("RELEVANCE_API_KEY", "sk-NDExNTgyOGItZTI1My00NGEzLWE1NGYtNDI0ZGE3ZjYwODUy")
RELEVANCE_REGION = os.getenv("RELEVANCE_REGION", "d7b62b")
TOOL_ID = "92f0d1e5-c44d-41c5-a05a-ae75c58941a2"

def health_reasoning(env, api_key=None):
    # Note: api_key arg is kept for backward compatibility but ignored in favor of env vars for Relevance
    
    try:
        # We use raw requests because the SDK trigger method was missing/unreliable in exploration
        url = f"https://api-{RELEVANCE_REGION}.stack.tryrelevance.com/latest/studios/{TOOL_ID}/trigger"
        
        headers = {
            "Authorization": f"{RELEVANCE_PROJECT}:{RELEVANCE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        **Environmental Data:**
        - AQI: {env.get('aqi')}
        - Temperature: {env.get('temperature')}°C
        - Humidity: {env.get('humidity')}%
        - Condition: {env.get('description')}
        
        **Pollutant Breakdown:**
        {env.get('pollutants')}

        **Task:**
        Provide a detailed health risk assessment in markdown format. Use the following structure:

        ### 📊 Executive Summary
        (2-3 sentences summarizing the overall air quality and weather impact)

        ### 🧪 Pollutant Analysis
        (Briefly explain the primary pollutants of concern based on the data, e.g., High PM2.5)

        ### 🩺 Health Implications
        (Specific risks for sensitive groups and general population)

        ### 🛡️ Actionable Advice
        (Bulleted list of specific recommendations: masks, outdoor activities, ventilation, hydration)
        """
        
        payload = {
            "params": {
                "prompt": prompt
            },
            "project": RELEVANCE_PROJECT
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return f"Health advice unavailable (Relevance AI Error: {response.status_code}). Data: {env}"
            
        data = response.json()
        
        # Extract advice from the specific path found in exploration
        # Path: output -> transformed -> advice
        # Fallback to full output if path doesn't exist
        advice = data.get("output", {}).get("transformed", {}).get("advice")
        
        if not advice:
             # Try alternative path just in case
             advice = data.get("output", {}).get("advice")
             
        if not advice:
            return f"Health advice unavailable (Parse Error). Raw: {str(data)}"
            
        return advice

    except Exception as e:
        return f"Health advice unavailable (Error: {str(e)}). Data: {env}"
