"""
Planner Agent - Generates actionable health plans based on AQI and risk levels.
"""
from datetime import datetime

def generate_daily_plan(env_data: dict, health_analysis: str | dict) -> dict:
    """
    Generate personalized daily health plan based on environment data and health analysis.
    """
    aqi = env_data.get('aqi', 0) or 0
    
    # Determine risk level
    if isinstance(health_analysis, dict):
        risk_level = health_analysis.get('risk_level', 'moderate')
    else:
        risk_level = 'moderate'
        if aqi > 150: risk_level = 'high'
        if aqi > 250: risk_level = 'severe'

    # Determine smoke arrival
    smoke_arrival = 24
    if isinstance(health_analysis, dict):
        smoke_arrival = health_analysis.get('smoke_arrival_hours', 24)

    fire_count = env_data.get('fire_count', 0)
    
    # Mask recommendations
    if aqi > 300:
        mask_level = "N95 (Mandatory)"
        mask_priority = "critical"
    elif aqi > 200:
        mask_level = "N95 (Highly Recommended)"
        mask_priority = "high"
    elif aqi > 150:
        mask_level = "N95 or KN95"
        mask_priority = "medium"
    elif aqi > 100:
        mask_level = "Surgical Mask"
        mask_priority = "low"
    else:
        mask_level = "Optional"
        mask_priority = "none"
    
    # Outdoor restrictions
    if aqi > 300:
        outdoor_restriction = "Complete restriction - Stay indoors"
        outdoor_allowed = False
    elif aqi > 200:
        outdoor_restriction = "Severe restriction - Only essential outdoor activities"
        outdoor_allowed = False
    elif aqi > 150:
        outdoor_restriction = "Moderate restriction - Limit outdoor time to 30 minutes"
        outdoor_allowed = True
    elif aqi > 100:
        outdoor_restriction = "Sensitive groups should limit outdoor time"
        outdoor_allowed = True
    else:
        outdoor_restriction = "Normal outdoor activities allowed"
        outdoor_allowed = True
    
    # Inhaler reminders
    inhaler_reminders = []
    breathlessness_risk = 0
    if isinstance(health_analysis, dict):
        breathlessness_risk = health_analysis.get('breathlessness_risk', 0)

    if risk_level in ['high', 'severe'] or breathlessness_risk > 6:
        inhaler_reminders = [
            "Morning: Use preventive inhaler before going out",
            "Evening: Keep rescue inhaler accessible"
        ]
    
    # Hydration
    hydration_ml = 2000
    if aqi > 200:
        hydration_ml = 3000
    elif aqi > 150:
        hydration_ml = 2500
    
    # Indoor purification
    purifier_recommendations = []
    if aqi > 150:
        purifier_recommendations.append("Run air purifier continuously")
        purifier_recommendations.append("Keep windows closed")
    elif aqi > 100:
        purifier_recommendations.append("Run air purifier during peak hours (10 AM - 6 PM)")
        purifier_recommendations.append("Close windows during high traffic hours")
    else:
        purifier_recommendations.append("Run air purifier 2-3 hours daily")
        purifier_recommendations.append("Ventilate during low pollution hours")
    
    # Stubble smoke action plan
    smoke_actions = []
    if fire_count > 0 and smoke_arrival < 12:
        smoke_actions.append(f"⚠️ Stubble smoke arriving in {smoke_arrival} hours")
        smoke_actions.append("Seal all windows and doors")
        smoke_actions.append("Run air purifier at maximum")
        smoke_actions.append("Avoid outdoor activities")
        smoke_actions.append("Use N95 mask if going out is necessary")
    
    # Extract AI-generated plan if available
    import re
    
    morning_plan = []
    afternoon_plan = []
    evening_plan = []
    
    # Try to parse the AI output
    if isinstance(health_analysis, str): # Use health_analysis as the source string
        # Regex to extract sections
        morning_match = re.search(r'### Morning Plan\s*(.*?)\s*(?=###|$)', health_analysis, re.DOTALL | re.IGNORECASE)
        afternoon_match = re.search(r'### Afternoon Plan\s*(.*?)\s*(?=###|$)', health_analysis, re.DOTALL | re.IGNORECASE)
        evening_match = re.search(r'### Evening Plan\s*(.*?)\s*(?=###|$)', health_analysis, re.DOTALL | re.IGNORECASE)
        
        def parse_plan_text(text):
            if not text: return ""
            # Return the full text, stripped of leading/trailing whitespace
            return text.strip()

        if morning_match:
            morning_plan = parse_plan_text(morning_match.group(1))
            
        if afternoon_match:
            afternoon_plan = parse_plan_text(afternoon_match.group(1))
            
        if evening_match:
            evening_plan = parse_plan_text(evening_match.group(1))

    # Fallback to rule-based logic if AI parsing failed or returned empty
    if not morning_plan:
        if aqi > 150:
            morning_plan = "**Avoid outdoor exercise.**\nKeep windows closed.\nUse air purifier if available."
        else:
            morning_plan = "**Good time for outdoor activities.**\nVentilate your home.\nEnjoy the fresh air."

    if not afternoon_plan:
        if aqi > 150:
            afternoon_plan = "**Stay indoors as much as possible.**\nWear a mask if you must go out.\nDrink plenty of water."
        else:
            afternoon_plan = "**Carry a mask just in case.**\nStay hydrated.\nMonitor AQI levels."

    if not evening_plan:
        if aqi > 150:
            evening_plan = "**Avoid evening walks.**\nRun air purifier in bedroom.\nEnsure windows are sealed."
        else:
            evening_plan = "**Safe for evening walk.**\nLight ventilation allowed.\nRelax and unwind."
    
    return {
        "mask_level": mask_level,
        "mask_priority": mask_priority,
        "outdoor_restriction": outdoor_restriction,
        "outdoor_allowed": outdoor_allowed,
        "inhaler_reminders": inhaler_reminders,
        "hydration_ml": hydration_ml,
        "purifier_recommendations": purifier_recommendations,
        "smoke_actions": smoke_actions,
        "morning_plan": morning_plan,
        "afternoon_plan": afternoon_plan,
        "evening_plan": evening_plan,
        "crisis_mode": aqi > 400
    }

def get_time_plan(time_of_day: str, aqi: int) -> list:
    """
    Get detailed, actionable plan for specific time of day based on AQI.
    """
    try:
        aqi = int(aqi)
    except (ValueError, TypeError):
        aqi = 0

    plans = {
        "morning": {
            "low_risk": [
                "✅ **Activity**: The air is relatively clean. It's a great time for an outdoor run or cycling session (6-8 AM).",
                "🥗 **Diet**: Start your day with a light, antioxidant-rich breakfast (berries, nuts).",
                "🏠 **Home**: Open windows to ventilate your home."
            ],
            "moderate_risk": [
                "⚠️ **Activity**: Limit intense outdoor cardio to 30 minutes. Prefer brisk walking.",
                "😷 **Protection**: Carry a mask. Wear it if you feel irritation.",
                "🥗 **Diet**: Drink warm water with lemon and honey."
            ],
            "high_risk": [
                "🚫 **Activity**: **SKIP outdoor exercise.** Switch to indoor yoga or home workouts.",
                "😷 **Protection**: **N95 mask is mandatory** if outdoors.",
                "💊 **Health**: Keep preventive inhaler handy if asthmatic.",
                "🥗 **Diet**: Consume Turmeric milk (Haldi Doodh) and Vitamin C rich foods."
            ]
        },
        "afternoon": {
            "low_risk": [
                "✅ **Activity**: Normal outdoor activities allowed.",
                "💧 **Hydration**: Aim for 2-3 liters of water throughout the day."
            ],
            "moderate_risk": [
                "⚠️ **Activity**: Avoid strenuous labor outdoors.",
                "🏠 **Home**: Keep windows closed during peak traffic (4-7 PM).",
                "💧 **Hydration**: Drink water every hour."
            ],
            "high_risk": [
                "🚫 **Activity**: **STAY INDOORS.** Avoid outdoor lunch breaks.",
                "🏠 **Home**: Run air purifier on **MAX**. Seal gaps under doors.",
                "🥗 **Diet**: Eat light meals (Salads, Soups).",
                "🚗 **Commute**: Use 'Recirculate' mode in car AC."
            ]
        },
        "evening": {
            "low_risk": [
                "✅ **Activity**: Evening walk in the park is safe.",
                "🏠 **Home**: Ventilate bedroom before sleeping."
            ],
            "moderate_risk": [
                "⚠️ **Activity**: Limit to a short walk. Avoid busy roads.",
                "🏠 **Home**: Run air purifier in bedroom for 1 hour before sleep."
            ],
            "high_risk": [
                "🚫 **Activity**: **No evening walks.** Pollution settles low at night.",
                "🏠 **Home**: Keep bedroom windows **sealed**. Air purifier ON.",
                "🚿 **Hygiene**: Wash face/hands immediately after returning home.",
                "🍵 **Diet**: Drink warm Ginger tea or soup."
            ]
        }
    }
    
    if aqi > 200:
        risk_category = "high_risk"
    elif aqi > 100:
        risk_category = "moderate_risk"
    else:
        risk_category = "low_risk"

    return plans.get(time_of_day, {}).get(risk_category, [])

def analyze_forecast(forecast: list) -> dict:
    """
    Analyzes the weekly AQI forecast to find best and worst days.
    """
    if not forecast:
        return {"best_day": "N/A", "worst_day": "N/A", "best_aqi": 0, "worst_aqi": 0}
        
    # Find min and max AQI
    min_aqi_item = min(forecast, key=lambda x: x['max_aqi'])
    max_aqi_item = max(forecast, key=lambda x: x['max_aqi'])
    
    return {
        "best_day": f"{min_aqi_item['day']} ({min_aqi_item['date']})",
        "best_aqi": min_aqi_item['max_aqi'],
        "worst_day": f"{max_aqi_item['day']} ({max_aqi_item['date']})",
        "worst_aqi": max_aqi_item['max_aqi']
    }
