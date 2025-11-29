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
    Provide a **comprehensive and detailed** health risk assessment and a **lengthy, actionable** daily routine in markdown format. Use the following structure:

    ### 📊 Executive Summary
    (Detailed summary of the overall air quality, weather impact, and what it means for the user's day.)

    ### 🧪 Pollutant Analysis
    (Explain the primary pollutants of concern, their sources, and why they are dangerous in this specific context.)

    ### 🩺 Health Implications
    (Detailed risks for sensitive groups (asthma, elderly, children) and the general population. Be specific.)

    ### 🛡️ Actionable Advice
    (Extensive list of recommendations: masks (type), outdoor activities (duration/intensity), ventilation (when/how), hydration (specific amounts).)

    ### 🌅 Morning Plan
    (Provide 3-4 detailed bullet points. Include specific advice on:
    - Commute precautions
    - Best time for ventilation (if any)
    - Morning exercise feasibility and intensity
    - Breakfast/Hydration tips for immunity)

    ### ☀️ Afternoon Plan
    (Provide 3-4 detailed bullet points. Focus on:
    - Managing peak heat/pollution hours
    - Work/School environment adjustments
    - Lunch choices for antioxidants
    - Hydration reminders)

    ### 🌙 Evening Plan
    (Provide 3-4 detailed bullet points. Cover:
    - Evening commute safety
    - Post-exposure cleanup (showering/washing)
    - Indoor air quality management for sleep
    - Relaxation techniques for respiratory health)
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
