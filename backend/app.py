from flask import Flask, render_template, request, jsonify
# Flask is a micro-framework that allows us to build web applications in Python.
# render_template: Sends HTML files to the user.
# request: Handles incoming data (like city name).
# jsonify: Converts Python dictionaries to JSON format (for APIs).

import os # Used to interact with the operating system (e.g., file paths)
import sys # Used to modify python path to find our custom modulest, send_from_directory
from dotenv import load_dotenv
import os
import sys

# Add root directory to path to find ai_models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_models.environment import get_environment_data, get_aqi_history, get_aqi_forecast, get_coordinates, calculate_cigarettes
from ai_models.advisory import get_health_advice, get_emergency_info
from ai_models.planner import generate_daily_plan, analyze_forecast
from ai_models.news import get_pollution_news

load_dotenv()
# Configure Flask to use paths in ../frontend
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# --- Routes ---

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    # Serve from the root 'assets' folder
    assets_path = os.path.join(os.path.dirname(app.root_path), 'assets')
    return send_from_directory(assets_path, filename)

@app.route('/favicon.ico')
def favicon():
    # Serve from assets/favicon.jpg
    assets_path = os.path.join(os.path.dirname(app.root_path), 'assets')
    return send_from_directory(assets_path, 'favicon.jpg', mimetype='image/jpeg')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/news")
def news_page():
    return render_template("news.html")

@app.route("/support")
def support_page():
    return render_template("support.html")

@app.route("/api/geocode")
def geocode():
    """Get coordinates for a city name."""
    city = request.args.get("city")
    country = request.args.get("country")
    
    if not city:
        return jsonify({"error": "City is required"}), 400
        
    locations = get_coordinates(city, country)
    return jsonify(locations)

@app.route("/api/environment/<lat>/<lon>")
def get_env(lat, lon):
    """
    Get full environment analysis: Weather, AQI, Health Advice, Plan, and News.
    """
    try:
        # Check for city override (e.g. from IP geolocation)
        override_city = request.args.get("city")

        # Raw data
        env_data = get_environment_data(lat, lon, override_city=override_city)
        # Calculate Cigarettes
        pm25 = env_data.get('pollutants', {}).get('PM2.5', {}).get('concentration', 0)
        cig_count = calculate_cigarettes(pm25)
        
        forecast_data = get_aqi_forecast(lat, lon)
        history_data = get_aqi_history(lat, lon)
        
    except Exception as e:
        return jsonify({"error": f"Environment data error: {str(e)}"}), 500

    # Initialize variables for AI/Local Analysis
    ai_result = {}
    health_text = "Health advice unavailable."
    plan = {}
    news_data = []
    emergency_info = {}
    forecast_analysis = {}

    # Emergency Info
    try:
        city = env_data.get('city', 'India')
        country = env_data.get('country', 'IN')
        emergency_info = get_emergency_info(city, country)
    except Exception as e:
        emergency_info = {"error": str(e)}

    # AI/Local Analysis
    try:
        ai_result = get_health_advice(env_data)
        health_text = ai_result.get("assessment", "Analysis unavailable.")
    except Exception as e:
        health_text = f"Health advice unavailable (Error: {str(e)})"

    try:
        plan = generate_daily_plan(env_data, ai_data=ai_result)
    except Exception as e:
        plan = {"error": f"Planner error: {str(e)}"}

    try:
        city = env_data.get('city', 'India')
        news_data = get_pollution_news(city)
    except Exception as e:
        news_data = []

    try:
        forecast_analysis = analyze_forecast(forecast_data)
    except Exception as e:
        forecast_analysis = {}

    return jsonify({
        "environment": env_data,
        "cigarette_equivalent": cig_count,
        "sources": ai_result.get("sources", []),
        "source_narrative": ai_result.get("source_narrative", "Source analysis unavailable."),
        "forecast": forecast_data,
        "history": history_data,
        "forecast_analysis": forecast_analysis,
        "health_advice": health_text,
        "daily_plan": plan,
        "news": news_data,
        "emergency_info": emergency_info
    })

@app.route('/api/news/<city>')
def get_city_news(city):
    try:
        news = get_pollution_news(city, limit=20)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/support')
def get_support_info():
    """Get emergency info for a location."""
    city = request.args.get('city')
    country = request.args.get('country')
    
    if not city:
        return jsonify({"error": "City required"}), 400
        
    info = get_emergency_info(city, country)
    return jsonify(info)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
