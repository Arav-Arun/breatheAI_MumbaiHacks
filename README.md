# 🌬️ BREATHAI - Agentic AI for India's Pollution Crisis

A comprehensive agentic AI system designed to help individuals navigate India's severe air pollution problem through intelligent, autonomous agents that collect data, reason about health impacts, plan actions, and learn from user feedback.

## 🎯 Features

### Core Agentic Architecture

1. **Environment Agent** - Collects real-time environmental data (AQI, PM2.5, weather, fire hotspots)
2. **Health Reasoning Agent** - LLM-powered health impact prediction
3. **Planner Agent** - Generates actionable daily health plans
4. **Notifier Agent** - Beautiful Streamlit UI with real-time alerts
5. **Community Health Agent** - Predicts hospital surge and community risk
6. **Feedback Agent** - Tracks user symptoms and refines predictions

### India/Delhi-Specific Features

- 🌫️ Hyperlocal pollution monitoring
- 🔥 Stubble smoke influx detection
- 🌅 Golden Hour outdoor window prediction
- 🏫 School Safety Mode
- 🏠 Indoor Air Advisor
- 🗺️ Anti-smog travel route advisor
- 🚨 Crisis Mode (AQI > 400)
- 🫁 Lung Recovery Companion
- 🏥 Hospital surge heatmap

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd MumbaiHacks
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Required API Keys

- **OpenAI API Key** - For Health Reasoning Agent (LLM)
- **OpenWeatherMap API Key** - For weather and air quality data
- **NASA FIRMS API Key** (Optional) - For fire hotspot detection
- **Google Maps API Key** (Optional) - For route planning

Get your keys:
- OpenAI: https://platform.openai.com/api-keys
- OpenWeatherMap: https://openweathermap.org/api
- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/api/

### Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
MumbaiHacks/
├── agents/
│   ├── environment_agent.py      # Data collection
│   ├── health_reasoning_agent.py  # LLM health analysis
│   ├── planner_agent.py          # Action planning
│   ├── community_health_agent.py  # Surge prediction
│   └── feedback_agent.py         # User feedback loop
├── app.py                        # Main Streamlit app
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
4. **Community Health Agent** predicts hospital surge using ML models
5. **Feedback Agent** learns from user symptoms to improve predictions
6. **Notifier Agent** (UI) presents everything in a beautiful, actionable format

## 🏆 Hackathon Highlights

- **Agentic Architecture** - Multiple autonomous agents working together
- **LLM Integration** - GPT-4 powered health reasoning
- **India-Focused** - Built specifically for Delhi/Mumbai pollution crisis
- **Beautiful UI** - Production-ready Streamlit interface
- **ML Models** - Hospital surge prediction using scikit-learn
- **Real-time Data** - Live API integration
- **User Feedback Loop** - Continuous learning system

## 📊 Tech Stack

- **Python** - Core language
- **Streamlit** - UI framework
- **OpenAI GPT-4** - LLM reasoning
- **OpenWeatherMap API** - Environmental data
- **Plotly** - Data visualization
- **Pandas** - Data processing
- **scikit-learn** - ML models

## 🎯 Future Enhancements

- [ ] Real-time mask fit detection using MediaPipe
- [ ] Google Maps integration for route planning
- [ ] Mobile app version
- [ ] Multi-city support with comparisons
- [ ] Historical trend analysis
- [ ] Community alerts and sharing
- [ ] Integration with wearable devices

## 📝 License

This project is created for MumbaiHacks hackathon.

## 👥 Team

Built with ❤️ for India's air quality crisis.

---

**🌬️ BREATHAI - Breathe Easy, Live Healthy**

