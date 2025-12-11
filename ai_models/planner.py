def _get_comprehensive_data(env: dict) -> dict:
    """
    Returns structured health advice based on local expert rules.
    Used by both the text generator and the daily planner fallback.
    """
    aqi = env.get('aqi', 0)
    
    # Determine Risk Level
    if aqi > 150: risk_level = "Hazardous"
    elif aqi > 100: risk_level = "Unhealthy"
    elif aqi > 50: risk_level = "Moderate"
    else: risk_level = "Good"
    
    # --- Content Templates ---
    if risk_level == "Hazardous":
        exec_summary = f"Air quality is critical (AQI {aqi}); strict indoor protocols are required to prevent acute respiratory distress."
        risks = """
*   **Acute Inflammation:** High PM2.5 loads can trigger immediate lung inflammation.
*   **Cardiovascular Stress:** Fine particles enter the bloodstream, potentially raising blood pressure.
*   **Cognitive Fog:** Reduced oxygen exchange efficiency may lead to headaches.
"""
        morning = "Avoid all outdoor exercise. Keep windows hermetically sealed. Use a wet mop to clean floors."
        afternoon = "Minimize any transit. Drink hot water. Place spider plants indoors."
        evening = "Sleep with an air purifier on. Do not open windows. Steam inhalation is recommended."
        
    elif risk_level == "Unhealthy":
        exec_summary = f"AQI is {aqi}; sensitive groups must avoid outdoor exposure, and everyone should limit exertion."
        risks = """
*   **Respiratory Irritation:** Likely throat scratching and coughing.
*   **Asthma Triggers:** High potential for triggering asthma attacks.
"""
        morning = "Skip the jog. Yoga indoors is safe. Vitamin C (Citrus) helps build resistance."
        afternoon = "Stay indoors during lunch. Drink water with lemon. Avoid aerosol sprays."
        evening = "Elevate your head slightly while sleeping if congested. Neti pot rinse is good."

    elif risk_level == "Moderate":
        exec_summary = f"Air quality is acceptable (AQI {aqi}); outdoor activity is okay, but sensitive people should be cautious."
        risks = """
*   **Minor Irritation:** Possible for extremely sensitive individuals.
"""
        morning = "Light jog is fine. Plan route through parks. Balanced breakfast."
        afternoon = "Normal activities. Green tea is good. Keep indoor humidity at 40-50%."
        evening = "Normal routine. Ensure bedroom is dust-free. Safe to open windows for short time."

    else: # GOOD
        exec_summary = f"Air quality is excellent (AQI {aqi}); enjoy the outdoors!"
        risks = """
*   **None:** The air is clean and healthy.
"""
        morning = "Go for a run! Open windows to flush stale air. Perfect for outdoor yoga."
        afternoon = "Spend time outside. Cognitive function is optimal. Have an outdoor lunch."
        evening = "Sleep with windows open (if quiet). Deep breathing exercises recommended."

    return {
        "assessment": f"### Current Status: AQI {aqi} ({risk_level})\n\n### Executive Summary\n{exec_summary}\n\n### Key Risks\n{risks}",
        "morning": morning,
        "afternoon": afternoon,
        "evening": evening
    }

def generate_comprehensive_plan(env: dict) -> str:
    """
    (Legacy Wrapper) Returns full markdown string.
    """
    data = _get_comprehensive_data(env)
    return f"""{data['assessment']}

### Morning Plan
{data['morning']}

### Afternoon Plan
{data['afternoon']}

### Evening Plan
{data['evening']}
"""

def generate_daily_plan(env: dict, ai_data: dict = None) -> dict:
    """
    Generates a personalized daily plan.
    Now uses robust fallback if ai_data is missing.
    """
    aqi = env.get('aqi', 0)
    
    # --- 1. LOCAL LOGIC: SAFETY METRICS ---
    if aqi > 300: mask_rec = "N95 (Mandatory)"
    elif aqi > 200: mask_rec = "N95 (Recommended)"
    elif aqi > 150: mask_rec = "Mask Required"
    elif aqi > 100: mask_rec = "Mask for Sensitive Groups"
    else: mask_rec = "Optional"
    
    if aqi > 200: hydration = "3.5 Liters"
    elif aqi > 150: hydration = "3 Liters"
    else: hydration = "2.5 Liters"

    # --- 2. SCHEDULE GENERATION ---
    morning_txt = "Advice unavailable."
    afternoon_txt = "Advice unavailable."
    evening_txt = "Advice unavailable."
    
    if ai_data:
        morning_txt = ai_data.get("morning_plan", "No specific morning plan.")
        afternoon_txt = ai_data.get("afternoon_plan", "No specific afternoon plan.")
        evening_txt = ai_data.get("evening_plan", "No specific evening plan.")
    else:
        # Fallback: Use structural data directly
        data = _get_comprehensive_data(env)
        morning_txt = data['morning']
        afternoon_txt = data['afternoon']
        evening_txt = data['evening']

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
        
    worst_item = max(forecast_data, key=lambda x: x['max_aqi'])
    best_item = min(forecast_data, key=lambda x: x['max_aqi'])
    
    return {
        "worst_day": f"{worst_item['day']} ({worst_item['date']})",
        "worst_aqi": worst_item['max_aqi'],
        "best_day": f"{best_item['day']} ({best_item['date']})",
        "best_aqi": best_item['max_aqi']
    }
