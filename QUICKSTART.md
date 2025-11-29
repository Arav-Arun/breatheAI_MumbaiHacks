# 🚀 Quick Start Guide

## For Hackathon Demo (Without API Keys)

The app works with **mock data** if API keys are not configured! Perfect for demos.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

That's it! The app will use simulated data and work perfectly for your hackathon presentation.

## For Full Functionality (With API Keys)

### 1. Get API Keys

- **OpenAI**: https://platform.openai.com/api-keys (Required for LLM reasoning)
- **OpenWeatherMap**: https://openweathermap.org/api (Free tier available)

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3. Run

```bash
streamlit run app.py
```

## Features to Demo

1. **Dashboard Tab** - Real-time AQI, pollution metrics, forecasts
2. **Health Tab** - Lung health score, risk analysis, daily plan
3. **Outdoors Tab** - Golden hour, mask recommendations, school safety
4. **Community Tab** - Hospital surge prediction, heatmaps
5. **Indoor Air Tab** - Purifier recommendations, recovery tips
6. **Feedback Tab** - Symptom logging, learning system

## Hackathon Presentation Tips

1. **Start with Dashboard** - Show real-time data collection
2. **Explain Agentic Architecture** - How agents work together
3. **Show Health Reasoning** - LLM-powered analysis
4. **Demonstrate Feedback Loop** - Log symptoms, show learning
5. **Highlight India Features** - Stubble smoke, golden hour, school safety

## Troubleshooting

- **No API keys?** App uses mock data automatically
- **Import errors?** Make sure all dependencies are installed
- **Port already in use?** Use `streamlit run app.py --server.port 8502`

---

**Good luck with your hackathon! 🌬️**

