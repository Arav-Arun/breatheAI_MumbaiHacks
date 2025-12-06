from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv
import os
import sys

from ai_models.environment import get_environment_data, get_aqi_history, get_aqi_forecast, get_coordinates
from ai_models.advisory import get_health_advice, get_emergency_info
from ai_models.planner import generate_daily_plan, analyze_forecast
from ai_models.news import get_pollution_news

load_dotenv()
app = Flask(__name__, static_folder='ui', static_url_path='/ui', template_folder='pages')

# --- Routes ---

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'assets'),
                               'favicon.jpg', mimetype='image/jpeg')

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
        # Raw data
        env_data = get_environment_data(lat, lon)
        forecast_data = get_aqi_forecast(lat, lon)
        history_data = get_aqi_history(lat, lon)
        
    except Exception as e:
        return jsonify({"error": f"Environment data error: {str(e)}"}), 500

    # AI Reasoning
    try:
        health = get_health_advice(env_data)
    except Exception as e:
        health = f"Health advice unavailable. Error: {str(e)}"

    # Planner
    daily_plan = {}
    forecast_analysis = {}
    news = []

    try:
        daily_plan = generate_daily_plan(env_data, health)
    except Exception as e:
        daily_plan = {"error": f"Planner error: {str(e)}"}

    try:
        forecast_analysis = analyze_forecast(forecast_data)
    except Exception as e:
        forecast_analysis = {}

    try:
        city = env_data.get('city', 'India')
        news = get_pollution_news(city)
    except Exception as e:
        news = []

    # Emergency Info
    emergency_info = {}
    try:
        city = env_data.get('city', 'India')
        country = env_data.get('country', 'IN')
        emergency_info = get_emergency_info(city, country)
    except Exception as e:
        emergency_info = {"error": str(e)}

    return jsonify({
        "environment": env_data,
        "forecast": forecast_data,
        "history": history_data,
        "forecast_analysis": forecast_analysis,
        "news": news,
        "health_advice": health,
        "news": news,
        "health_advice": health,
        "daily_plan": daily_plan,
        "emergency_info": emergency_info
    })

application = app

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
