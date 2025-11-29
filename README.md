# 🌬️ BreathAI - Clarity in every breath
A comprehensive agentic AI system designed to help individuals navigate India's severe air pollution problem through intelligent, autonomous agents that collect data, reason about health impacts, plan actions, and learn from user feedback.

## 🎯 Features

### Core Agentic Architecture

1. **Environment Agent** - Collects real time environmental data (AQI, PM2.5, weather, fire hotspots)
2. **Health Reasoning Agent** - LLM-powered health impact prediction
3. **Planner Agent** - Generates actionable daily health plans

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <https://github.com/Arav-Arun/breatheAI_MumbaiHacks.git>
cd MumbaiHacks
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

### Required API Keys

- **Relevance API Key** - For Health Reasoning Agent (LLM)
- **OpenWeatherMap API Key** - For weather and air quality data
- **NASA FIRMS API Key** - For fire hotspot detection
- **Google Maps API Key**  - For route planning

Get your keys:
- OpenAI: https://relevanceai.com/
- OpenWeatherMap: https://openweathermap.org/api
- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/api/

## 📁 Project Structure

```
MumbaiHacks/
├── agents/
│   ├── environment_agent.py      # Data collection
│   ├── health_reasoning_agent.py  # LLM health analysis
│   ├── planner_agent.py          # Action planning
│   ├── community_health_agent.py  # Surge prediction
│   └── feedback_agent.py         # User feedback loop
├── app.py                        # Main app
├── config.py                     # Configuration
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🎨 UI Features

- **Wide Layout** - Optimized for data visualization
- **Color-Coded AQI** - Visual indicators for air quality levels
- **Interactive Charts** - Plotly graphs for trends and forecasts
- **Crisis Mode** - Special UI for severe pollution (AQI > 400)
- **Tabbed Interface** - Organized by user flows
- **Real-time Updates** - Live data refresh
- **Responsive Design** - Works on desktop and tablet

## 🔧 Configuration

Edit `config.py` to customize:
- Default location (latitude/longitude)
- AQI color scheme
- AQI thresholds
- Hospital locations

## 🤖 How It Works

1. **Environment Agent** collects real-time pollution and weather data
2. **Health Reasoning Agent** (LLM) analyzes health impact based on user profile
3. **Planner Agent** generates personalized daily recommendations

## 🏆 Hackathon Highlights

- **Agentic Architecture** - Multiple autonomous agents working together
- **Relevance LLM Integration** – Fast, reliable health reasoning
- **Beautiful UI** - Production-ready Streamlit interface
- **ML Models** - Hospital surge prediction using scikit-learn
- **Real-time Data** - Live API integration
- **User Feedback Loop** - Continuous learning system

## 📊 Tech Stack

- **Python** - Core language
- **Streamlit** - UI framework
- **Relevance AI LLM** - LLM reasoning
- **OpenWeatherMap API** - Environmental data
- **Plotly** - Data visualization
- **Pandas** - Data processing
- **scikit-learn** - ML models


## 👥 Team

Built with ❤️ by team TetraBytes for Mumbai Hacks 2025.

