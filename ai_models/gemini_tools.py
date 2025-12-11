import google.generativeai as genai
import os
import json
from ai_models.advisory import GEMINI_API_KEY

# Configure GenAI
genai.configure(api_key=GEMINI_API_KEY)

# Reuse the same model version for consistency
MODEL_NAME = "gemini-1.5-flash-latest" 
# Or if that fails again (it worked in test), fallback to 'gemini-pro' logic handled by caller? 
# No, we assume it works now.

def analyze_image_quality(image_bytes, env_context):
    """
    Analyzes an uploaded image of the sky/environment.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        prompt = f"""
        You are an air quality expert. Analyze this image of the sky/street.
        Current Sensor Data for context:
        AQI: {env_context.get('aqi')}
        City: {env_context.get('city')}
        
        Task:
        1. Estimate visibility (in km).
        2. Describe the haze/smog intensity (None, Mild, Heavy, Serve).
        3. Compare visual cues with the sensor AQI (Does it look better/worse?).
        
        Keep it brief (3-4 sentences).
        """
        
        # Create image blob
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        return f"Image analysis failed: {str(e)}"

def chat_with_ai(query, env_context):
    """
    Context-aware chat about air quality.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        aqi = env_context.get('aqi')
        prompt = f"""
        System: You are 'BreatheAI Assistant', a helpful Air Quality expert.
        Context: User is in {env_context.get('city')} where AQI is {aqi} ({env_context.get('risk_level', 'Unknown')}).
        Temperature: {env_context.get('temperature')}C.
        
        User Query: "{query}"
        
        Answer elegantly and concisely. If they ask about running/activity, use the AQI to decide.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I couldn't process that. Error: {str(e)}"

def get_commute_advice(env_context, forecast_series=None):
    """
    Analyzes forecast to suggest commute times.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Simplify forecast data for prompt
        forecast_str = "No hourly forecast available."
        if forecast_series:
            # Take next 5 steps (assuming approx 3-hour blocks usually, or just day blocks)
            # data structure of forecast_series needs checking. Assuming list of dicts.
            forecast_str = str(forecast_series[:5]) 
            
        prompt = f"""
        Task: Analyze the commute conditions for the next 24 hours.
        Current AQI: {env_context.get('aqi')}.
        Forecast Snippet: {forecast_str}
        
        Output a "Commute Recommendation":
        1. Best time to leave (if variance exists).
        2. Mode of transport tip (Windows up/down, Mask etc).
        
        Keep it short (2 sentences).
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Commute advice unavailable."

def compare_history(env_context, history_data=None):
    """
    Compares today to historical data.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        history_str = str(history_data) if history_data else "No history data."
        
        prompt = f"""
        Task: "Time Machine" comparison.
        Current AQI: {env_context.get('aqi')}.
        Historical Data (Past few days/years): {history_str}
        
        Tell the user if today is better or worse than usual for this location.
        Be interesting.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Historical comparison unavailable."
