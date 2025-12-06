"""
Planner Agent - Generates actionable health plans based on AQI and risk levels using Gemini.
"""
import re

def generate_daily_plan(env: dict, health_advice: str) -> dict:
    """
    Generates a personalized daily plan using pure logic (Instant).
    No external AI calls to ensure maximum speed.
    """
    aqi = env.get('aqi', 0)
    
    # --- 1. SAFETY METRICS ---
    if aqi > 300: mask_rec = "N95 (Mandatory)"
    elif aqi > 200: mask_rec = "N95 (Recommended)"
    elif aqi > 150: mask_rec = "Mask Required"
    elif aqi > 100: mask_rec = "Mask for Sensitive Groups"
    else: mask_rec = "Optional"
    
    if aqi > 200: hydration = "3.5 Liters"
    elif aqi > 150: hydration = "3 Liters"
    else: hydration = "2.5 Liters"

    # --- 2. SCHEDULE GENERATION (Rule-Based Paragraphs) ---
    # We prioritize the detailed paragraphs the user requested.
    
    if aqi > 150:
        morning_txt = "**Avoid outdoor exercise.**\n\nThe air quality is currently poor, with high levels of particulate matter. Engaging in strenuous activity outdoors can lead to deep inhalation of these pollutants, causing respiratory stress. Instead, opt for indoor activities like yoga or light stretching in a filtered environment. Keep windows closed to prevent pollutant entry."
        afternoon_txt = "**Stay indoors and protect yourself.**\n\nPollution levels often peak or remain high during the day. If you must go out, wearing an N95 mask is highly recommended to filter out harmful particles. Use an air purifier if available in your workspace or home to maintain healthy indoor air quality."
        evening_txt = "**No evening walks.**\n\nPollutants often settle near the ground at night due to cooling temperatures. Avoid evening walks to prevent exposure. Run an air purifier in your bedroom to ensure you sleep in clean air, which is crucial for overnight recovery."
    elif aqi > 100:
        morning_txt = "**Light activity only.**\n\nAir quality is moderate but sensitive groups should be careful. A short walk is okay, but avoid heavy running. Wear a mask if you have asthma or other respiratory conditions."
        afternoon_txt = "**Monitor conditions.**\n\nKeep an eye on the AQI. If it rises, move indoors. Ensure you are drinking plenty of water to help your body cope with any inhaled particulates."
        evening_txt = "**Limit outdoor exposure.**\n\nIt's best to relax indoors this evening. If you do go out, keep it brief. Ensure your sleeping area is well-ventilated if the outside air improves, otherwise keep windows shut."
    else:
        morning_txt = "**Good for outdoor activities.**\n\nThe air quality is relatively good this morning. It is a great time for a jog or a brisk walk in the park. Fresh air can boost your energy levels and improve mental clarity. Ensure you ventilate your home by opening windows to let fresh air circulate."
        afternoon_txt = "**Moderate activity allowed.**\n\nWhile the air is acceptable, continue to monitor changes. Stay hydrated to help your body flush out any toxins. It is safe to keep windows open for cross-ventilation, but be mindful if you live near heavy traffic."
        evening_txt = "**Safe for evening strolls.**\n\nThe evening air is pleasant and safe. A post-dinner walk can aid digestion and help you relax. Ensure good sleep hygiene by keeping your bedroom well-ventilated and comfortable."

    return {
        "mask_level": mask_rec,
        "hydration_ml": hydration,
        "morning_plan": morning_txt,
        "afternoon_plan": afternoon_txt,
        "evening_plan": evening_txt
    }

def analyze_forecast(forecast_data):
    """
    Analyzes the 5-day forecast to find the best and worst days.
    """
    if not forecast_data:
        return {}
        
    # Find day with max AQI
    worst_item = max(forecast_data, key=lambda x: x['max_aqi'])
    # Find day with min AQI
    best_item = min(forecast_data, key=lambda x: x['max_aqi'])
    
    return {
        "worst_day": f"{worst_item['day']} ({worst_item['date']})",
        "worst_aqi": worst_item['max_aqi'],
        "best_day": f"{best_item['day']} ({best_item['date']})",
        "best_aqi": best_item['max_aqi']
    }
