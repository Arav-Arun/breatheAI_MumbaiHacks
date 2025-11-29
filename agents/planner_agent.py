"""
Planner Agent - Generates actionable health plans
"""
from datetime import datetime, timedelta

class PlannerAgent:
    def __init__(self):
        pass
    
        """Generate personalized daily health plan"""
        aqi = env_data.get('aqi')
        if aqi is None:
            aqi = 0
        
        # Robustly handle health_analysis being a string or dict
        if isinstance(health_analysis, str):
            risk_level = 'moderate' # Default
            if aqi > 150: risk_level = 'high'
            if aqi > 250: risk_level = 'severe'
        else:
            risk_level = health_analysis.get('risk_level', 'moderate')

        smoke_arrival = 24 # Default
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
        
        # Golden hour prediction
        golden_hour = self.predict_golden_hour(env_data)
        
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
        
        # Time-based plan
        morning_plan = self.get_time_plan("morning", aqi, golden_hour)
        afternoon_plan = self.get_time_plan("afternoon", aqi, golden_hour)
        evening_plan = self.get_time_plan("evening", aqi, golden_hour)
        
        return {
            "mask_level": mask_level,
            "mask_priority": mask_priority,
            "outdoor_restriction": outdoor_restriction,
            "outdoor_allowed": outdoor_allowed,
            "inhaler_reminders": inhaler_reminders,
            "hydration_ml": hydration_ml,
            "purifier_recommendations": purifier_recommendations,
            "smoke_actions": smoke_actions,
            "golden_hour": golden_hour,
            "morning_plan": morning_plan,
            "afternoon_plan": afternoon_plan,
            "evening_plan": evening_plan,
            "crisis_mode": aqi > 400
        }
    
    def predict_golden_hour(self, env_data):
        """Predict the best time window for outdoor activities"""
        hourly_aqi = env_data.get('hourly_aqi', [])
        
        if not hourly_aqi:
            return {
                "start": "6:00 AM",
                "end": "8:00 AM",
                "aqi": 120,
                "available": True
            }
        
        # Find the window with lowest AQI in next 12 hours
        min_aqi = min([h.get('aqi', 200) for h in hourly_aqi])
        best_hour = next((h for h in hourly_aqi if h.get('aqi') == min_aqi), hourly_aqi[0])
        
        best_time = best_hour.get('time', datetime.now())
        if isinstance(best_time, str):
            best_time = datetime.now()
        
        return {
            "start": (best_time - timedelta(hours=1)).strftime("%I:%M %p"),
            "end": (best_time + timedelta(hours=2)).strftime("%I:%M %p"),
            "aqi": int(min_aqi),
            "available": min_aqi < 150
        }
    
    def get_time_plan(self, time_of_day, aqi, golden_hour):
        """Get detailed, actionable plan for specific time of day"""
        # Ensure AQI is an integer to prevent errors
        try:
            aqi = int(aqi)
        except (ValueError, TypeError):
            aqi = 0

        plans = {
            "morning": {
                "low_risk": [
                    "✅ **Activity**: The air is relatively clean. It's a great time for an outdoor run or cycling session (6-8 AM) to boost your metabolism.",
                    "🥗 **Diet**: Start your day with a light, antioxidant-rich breakfast. Include fruits like berries and nuts to support your immune system.",
                    "🏠 **Home**: Open your windows wide to let in fresh air and ventilate your home, reducing indoor CO2 levels."
                ],
                "moderate_risk": [
                    "⚠️ **Activity**: Air quality is acceptable but not perfect. Limit intense outdoor cardio to 30 minutes. Prefer brisk walking over running.",
                    "😷 **Protection**: It's wise to carry a mask with you. If you feel any irritation, wear it immediately.",
                    "🥗 **Diet**: Drink warm water with lemon and honey. This helps clear your airways and soothes the throat against potential pollutants."
                ],
                "high_risk": [
                    "🚫 **Activity**: **SKIP outdoor exercise.** The air is toxic. Switch to indoor yoga, stretching, or a home workout routine.",
                    "😷 **Protection**: If you must go out, wearing an **N95 mask is mandatory**. Ensure a tight seal around your nose and mouth.",
                    "💊 **Health**: Keep your preventive inhaler handy if you have asthma. Steam inhalation with eucalyptus oil is highly recommended to clear nasal passages.",
                    "🥗 **Diet**: Consume Turmeric milk (Haldi Doodh) and foods rich in Vitamin C and E to fight oxidative stress caused by pollution."
                ]
            },
            "afternoon": {
                "low_risk": [
                    "✅ **Activity**: Conditions are good. Normal outdoor activities are allowed. Enjoy the sunshine!",
                    "💧 **Hydration**: Stay hydrated. Aim for 2-3 liters of water throughout the day to keep your mucous membranes moist and effective."
                ],
                "moderate_risk": [
                    "⚠️ **Activity**: Avoid strenuous labor or heavy exercise outdoors. The heat combined with moderate pollution can be taxing.",
                    "🏠 **Home**: Keep windows closed during peak traffic hours (usually 4-7 PM) to prevent exhaust fumes from entering.",
                    "💧 **Hydration**: Drink a glass of water every hour. Hydration helps your kidneys flush out toxins absorbed from the environment."
                ],
                "high_risk": [
                    "🚫 **Activity**: **STAY INDOORS.** Do not take outdoor lunch breaks. Walk inside your office or home if you need to move.",
                    "🏠 **Home**: Run your air purifier on **MAX mode**. Use rolled-up towels to seal gaps under doors to prevent smoke infiltration.",
                    "🥗 **Diet**: Eat a light lunch (Salads, Soups). Heavy meals increase metabolic stress, which is already high due to pollution.",
                    "🚗 **Commute**: If driving, ensure your car AC is set to **'Recirculate' mode** to avoid pulling in outside air."
                ]
            },
            "evening": {
                "low_risk": [
                    "✅ **Activity**: The air has settled. An evening walk in the park is safe and recommended for mental relaxation.",
                    "🏠 **Home**: Ventilate your bedroom for 15-20 minutes before sleeping to ensure a fresh supply of oxygen."
                ],
                "moderate_risk": [
                    "⚠️ **Activity**: Limit yourself to a short walk. Avoid busy roads or intersections where vehicle emissions are highest.",
                    "🏠 **Home**: Run your air purifier in the bedroom for at least 1 hour before sleep to create a clean sleep environment."
                ],
                "high_risk": [
                    "🚫 **Activity**: **No evening walks.** The pollution layer settles low at night. Stick to indoor family time or reading.",
                    "🏠 **Home**: Keep bedroom windows **strictly sealed**. Keep the air purifier ON throughout the night for safe sleep.",
                    "🚿 **Hygiene**: Wash your face and hands thoroughly immediately after returning home to remove particulate matter from your skin.",
                    "🍵 **Diet**: Drink warm Ginger tea or a soothing soup. This helps reduce inflammation in the throat and lungs."
                ]
            }
        }
        
        # Determine risk category
        if aqi > 200:
            risk_category = "high_risk"
        elif aqi > 100:
            risk_category = "moderate_risk"
        else:
            risk_category = "low_risk"

        base_plan = plans.get(time_of_day, {}).get(risk_category, [])
        
        # Add golden hour info for morning
        if time_of_day == "morning" and golden_hour.get('available'):
            base_plan.insert(0, f"🌅 **Golden Hour**: {golden_hour['start']} - {golden_hour['end']} (Best time for outdoors)")
        
        return base_plan

