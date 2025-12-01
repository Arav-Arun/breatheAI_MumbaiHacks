from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
import sys

# Ensure imports work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.environment_agent import get_environment_data, get_aqi_history, get_aqi_forecast, get_coordinates, get_micro_aqi
from ai.reasoning_agent import health_reasoning
from ai.planner_agent import generate_daily_plan, analyze_forecast
from ai.news_agent import get_pollution_news

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__, 
            template_folder='../frontend/templates', 
            static_folder='../frontend/static')

# --- Routes ---

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
        micro_data = get_micro_aqi(lat, lon)
        forecast_data = get_aqi_forecast(lat, lon)
        history_data = get_aqi_history(lat, lon)
        
    except Exception as e:
        return jsonify({"error": f"Environment data error: {str(e)}"}), 500

    # AI Reasoning
    try:
        health = health_reasoning(env_data)
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

    return jsonify({
        "environment": env_data,
        "micro_aqi": micro_data,
        "forecast": forecast_data,
        "history": history_data,
        "forecast_analysis": forecast_analysis,
        "news": news,
        "health_advice": health,
        "daily_plan": daily_plan
    })

application = app

@app.route('/api/news/<city>')
def get_city_news(city):
    try:
        news = get_pollution_news(city, limit=20)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
