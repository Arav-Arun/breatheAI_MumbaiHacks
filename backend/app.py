from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
import sys

# Add the current directory (backend) to sys.path to ensure imports work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom agent modules
# Note: Since we are running this from the backend directory (or as a package), 
# and 'ai' is in the same directory, we import directly from 'ai'.
from ai.environment_agent import get_environment_data, get_aqi_history, get_aqi_forecast, get_coordinates, get_micro_aqi
from ai.reasoning_agent import health_reasoning
from ai.planner_agent import generate_daily_plan, analyze_forecast
from ai.news_agent import get_pollution_news

# Load environment variables (API keys) from the .env file
# We explicitly point to the .env file in the parent directory to be safe
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Initialize the Flask application
# We need to tell Flask where the frontend files are located relative to this file
# app.py is in /backend
# templates are in /frontend/templates (so ../frontend/templates)
# static files are in /frontend/static (so ../frontend/static)
app = Flask(__name__, 
            template_folder='../frontend/templates', 
            static_folder='../frontend/static')

# --- Routes ---

@app.route("/")
def home():
    """
    The main homepage route.
    Returns the index.html template when a user visits the root URL ('/').
    """
    return render_template("index.html")

@app.route("/news")
def news_page():
    """
    The dedicated news page route.
    """
    return render_template("news.html")

@app.route("/support")
def support_page():
    """
    The respiratory support directory page.
    """
    return render_template("support.html")

@app.route("/api/geocode")
def geocode():
    """
    API Route: Get latitude and longitude for a city name.
    Example usage: /api/geocode?city=London&country=GB
    """
    # Get city and country from the URL parameters
    city = request.args.get("city")
    country = request.args.get("country")
    
    # Check if city is provided
    if not city:
        return jsonify({"error": "City is required"}), 400
        
    # Call our helper function to get coordinates
    locations = get_coordinates(city, country)
    
    # Return the result as JSON
    return jsonify(locations)

@app.route("/api/environment/<lat>/<lon>")
def get_env(lat, lon):
    """
    API Route: Get full environment analysis.
    1. Fetches Weather & AQI data.
    2. Uses AI to reason about health risks.
    3. Generates a daily plan based on the data.
    4. Generates Micro-Zone AQI map data.
    5. Generates 5-day AQI Forecast & History.
    6. Fetches Local Pollution News.
    """
    try:
        # Step 1: Get raw environment data (Weather + Air Quality)
        env_data = get_environment_data(lat, lon)
        
        # Step 1.5: Get Micro-Zone Data & Forecast
        micro_data = get_micro_aqi(lat, lon)
        forecast_data = get_aqi_forecast(lat, lon)
        history_data = get_aqi_history(lat, lon)
        
    except Exception as e:
        # If something goes wrong, return a 500 error
        return jsonify({"error": f"Environment data error: {str(e)}"}), 500

    # Step 2: Get Health Advice (AI Reasoning)
    try:
        health = health_reasoning(env_data)
    except Exception as e:
        health = f"Health advice unavailable. Error: {str(e)}"

    # Step 3: Generate a Daily Plan (Actionable Steps)
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
        # Fetch News
        city = env_data.get('city', 'India')
        news = get_pollution_news(city)
    except Exception as e:
        news = []

    # Combine everything into one response
    response = {
        "environment": env_data,
        "micro_aqi": micro_data,
        "forecast": forecast_data,
        "history": history_data,
        "forecast_analysis": forecast_analysis,
        "news": news,
        "health_advice": health,
        "daily_plan": daily_plan
    }
    
    # Return as JSON
    return jsonify(response)

# Export 'application' for Vercel deployment
application = app

@app.route('/api/news/<city>')
def get_city_news(city):
    try:
        # Fetch 20 news items for the dedicated page
        news = get_pollution_news(city, limit=20)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
