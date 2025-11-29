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
    Provide a detailed, scientifically-backed daily health plan in markdown.

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
