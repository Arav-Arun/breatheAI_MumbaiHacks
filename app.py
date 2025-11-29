from flask import Flask, render_template, jsonify, request
from agents.environment_agent import get_environment_data, get_coordinates
from agents.reasoning_agent import health_reasoning
from agents.planner_agent import PlannerAgent
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
planner = PlannerAgent()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/geocode")
def geocode():
    city = request.args.get("city")
    country = request.args.get("country")
    
    if not city:
        return jsonify({"error": "City is required"}), 400
        
    locations = get_coordinates(city, country)
    return jsonify(locations)

@app.route("/api/environment/<lat>/<lon>")
def get_env(lat, lon):
    try:
        env_data = get_environment_data(lat, lon)
    except Exception as e:
        return jsonify({"error": f"Environment data error: {str(e)}"}), 500

    try:
        health = health_reasoning(env_data)
    except Exception as e:
        health = "Health advice unavailable (Check OpenAI API Key). Data: " + str(env_data)

    response = {
        "environment": env_data,
        "health_advice": health,
        "daily_plan": planner.generate_daily_plan(env_data, health)
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

# Export the Flask app for Vercel
application = app
