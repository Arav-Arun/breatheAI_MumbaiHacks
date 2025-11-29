import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Relevance AI Configuration
RELEVANCE_PROJECT = os.getenv("RELEVANCE_PROJECT")
RELEVANCE_API_KEY = os.getenv("RELEVANCE_API_KEY")
RELEVANCE_REGION = os.getenv("RELEVANCE_REGION", "d7b62b")
TOOL_ID = "92f0d1e5-c44d-41c5-a05a-ae75c58941a2"

def health_reasoning(env: dict) -> str:
    """
    Generates health advice based on environmental data using Relevance AI.
    """
    try:
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
    Provide a detailed health risk assessment and a daily routine in markdown format. Use the following structure:

    ### 📊 Executive Summary
    (2-3 sentences summarizing the overall air quality and weather impact)

    ### 🧪 Pollutant Analysis
    (Briefly explain the primary pollutants of concern based on the data, e.g., High PM2.5)

    ### 🩺 Health Implications
    (Specific risks for sensitive groups and general population)

    ### 🛡️ Actionable Advice
    (Bulleted list of specific recommendations: masks, outdoor activities, ventilation, hydration)

    ### 🌅 Morning Plan
    (Specific advice for morning activities, commute, and ventilation. Be detailed.)

    ### ☀️ Afternoon Plan
    (Advice for the hottest/busiest part of the day. Work/School adjustments.)

    ### 🌙 Evening Plan
    (Advice for evening commute, exercise, and sleep environment.)
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
