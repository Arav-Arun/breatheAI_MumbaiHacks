// Load countries on start
window.onload = async function () {
  // Check for city param to restore state (e.g. from News page back button)
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const cityParam = urlParams.get("city");

    if (cityParam) {
      document.getElementById("city-input").value = cityParam;
      searchLocation();
      return; // Skip country load or load in background
    }
  } catch (e) {
    console.error("URL param parsing error", e);
  }

  try {
    const response = await fetch(
      "https://restcountries.com/v3.1/all?fields=name,cca2"
    );
    const data = await response.json();

    const select = document.getElementById("country-select");
    select.innerHTML = '<option value="">Country</option>';

    data.sort((a, b) => a.name.common.localeCompare(b.name.common));

    data.forEach((country) => {
      const option = document.createElement("option");
      option.value = country.cca2;
      option.text = country.name.common;
      select.appendChild(option);
    });
  } catch (e) {
    console.error("Failed to load countries", e);
    document.getElementById("country-select").innerHTML =
      '<option value="">Error</option>';
  }
};

function getLocation() {
  showLoading();
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(fetchData, showError, {
      enableHighAccuracy: false,
      timeout: 15000,
      maximumAge: 0,
    });
  } else {
    alert("Geolocation is not supported by this browser.");
    hideLoading();
  }
}

async function searchLocation() {
  const city = document.getElementById("city-input").value;
  const country = document.getElementById("country-select").value;
  const resultsDiv = document.getElementById("search-results");
  const errorDiv = document.getElementById("search-error");

  // Reset UI
  resultsDiv.style.display = "none";
  if (errorDiv) {
    errorDiv.style.display = "none";
    errorDiv.innerText = "";
  }

  if (!city) {
    if (errorDiv) {
      errorDiv.innerText = "Please enter a city name";
      errorDiv.style.display = "block";
    } else {
      alert("Please enter a city name");
    }
    return;
  }

  showLoading();

  try {
    const response = await fetch(
      `/api/geocode?city=${encodeURIComponent(city)}&country=${country}`
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Server Error ${response.status}: ${errorText.substring(0, 100)}`
      );
    }

    let data;
    const text = await response.text();
    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(`Invalid JSON response: ${text.substring(0, 100)}...`);
    }

    hideLoading();

    if (data.error) {
      if (errorDiv) {
        errorDiv.innerText = data.error;
        errorDiv.style.display = "block";
      } else {
        alert(data.error);
      }
      return;
    }

    if (data.length === 0) {
      if (errorDiv) {
        errorDiv.innerText = "Location not found. Please try another query.";
        errorDiv.style.display = "block";
      } else {
        alert("No locations found.");
      }
      return;
    }

    if (data.length === 1) {
      selectLocation(data[0]);
    } else {
      resultsDiv.innerHTML = "";
      data.forEach((loc) => {
        const div = document.createElement("div");
        div.className = "result-item";
        div.innerText = `${loc.name}, ${loc.state ? loc.state + ", " : ""}${
          loc.country
        }`;
        div.onclick = () => selectLocation(loc);
        resultsDiv.appendChild(div);
      });
      resultsDiv.style.display = "flex";
    }
  } catch (e) {
    console.error("Search Error:", e);
    hideLoading();
    if (errorDiv) {
      errorDiv.innerText = "Error: " + e.message;
      errorDiv.style.display = "block";
    } else {
      alert("Search Error: " + e);
    }
  }
}

function selectLocation(loc) {
  document.getElementById("search-results").style.display = "none";
  const position = {
    coords: {
      latitude: loc.lat,
      longitude: loc.lon,
    },
  };
  fetchData(position, loc.name);
}

function showLoading() {
  document.body.classList.remove("landing-mode");
  document.getElementById("loading").style.display = "flex";
  document.getElementById("dashboard").style.display = "none";
}

function hideLoading() {
  document.getElementById("loading").style.display = "none";
}

function showError(error) {
  let msg = "An unknown error occurred.";
  let tryIpFallback = false;

  switch (error.code) {
    case error.PERMISSION_DENIED:
      msg = "User denied the request for Geolocation.";
      break;
    case error.POSITION_UNAVAILABLE:
      msg = "Location information is unavailable.";
      tryIpFallback = true;
      break;
    case error.TIMEOUT:
      msg = "The request to get user location timed out.";
      tryIpFallback = true;
      break;
    case error.UNKNOWN_ERROR:
      msg = "An unknown error occurred.";
      tryIpFallback = true;
      break;
  }

  if (tryIpFallback) {
    console.log(
      "Browser geolocation failed (" + msg + "). Trying IP fallback..."
    );
    getIpLocation();
  } else {
    alert(
      `LOCATION ERROR: ${msg}\n\nPlease use the search bar to find your city manually.`
    );
    hideLoading();
  }
}

async function getIpLocation() {
  try {
    const response = await fetch("https://ipapi.co/json/");
    if (!response.ok) throw new Error("IP API failed");
    const data = await response.json();

    if (data.latitude && data.longitude) {
      const position = {
        coords: {
          latitude: data.latitude,
          longitude: data.longitude,
        },
      };
      // Add a small notification so user knows it's approximate
      const dash = document.getElementById("dashboard"); // Just to ensure we're on the page
      fetchData(position, data.city);
    } else {
      throw new Error("Invalid IP data");
    }
  } catch (e) {
    console.error("IP Fallback failed:", e);
    alert(
      "LOCATION ERROR: Unable to detect location via GPS or IP.\n\nPlease use the search bar to find your city manually."
    );
    hideLoading();
  }
}

async function fetchData(position, cityName = null) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;

  showLoading();

  try {
    let url = `/api/environment/${lat}/${lon}`;
    if (cityName) {
      url += `?city=${encodeURIComponent(cityName)}`;
    }

    const response = await fetch(url);
    if (!response.ok) throw new Error("Environment API failed");

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    hideLoading();
    document.getElementById("dashboard").style.display = "grid";

    // 1. Render immediate data (Weather, AQI, Charts)
    updateDashboard(data);

    // 2. Async waterfall for secondary data
    const env = data.environment;

    // Trigger independent background fetches
    // News is fetched with limit=5 for dashboard consistency
    fetchNews(env.city);
    fetchSupport(env.city, env.country);
    fetchAdvisory(env);
  } catch (e) {
    alert("Error: " + e.message);
    hideLoading();
  }
}

async function fetchNews(city) {
  const container = document.getElementById("news-container");
  if (!city) return;

  try {
    const res = await fetch(`/api/news/${encodeURIComponent(city)}`);
    const news = await res.json();

    if (news && news.length > 0) {
      container.innerHTML = "";
      news.forEach((item) => {
        const div = document.createElement("div");
        div.className = "news-item";
        div.innerHTML = `
                    <a href="${item.link}" target="_blank">${item.title}</a>
                    <span class="news-source">${item.source} • ${item.date}</span>
                `;
        container.appendChild(div);
      });
      // Update Show More
      const showMore = document.getElementById("show-more-news");
      if (showMore) showMore.href = `/news?city=${encodeURIComponent(city)}`;
    } else {
      container.innerHTML =
        '<div style="color: rgba(255,255,255,0.5);">No recent news.</div>';
    }
  } catch (e) {
    container.innerHTML =
      '<div style="color: #fca5a5;">Failed to load news.</div>';
  }
}

async function fetchSupport(city, country) {
  try {
    const res = await fetch(
      `/api/support?city=${encodeURIComponent(
        city
      )}&country=${encodeURIComponent(country)}`
    );
    const info = await res.json();

    if (info && !info.error) {
      document.getElementById("emerg-ambulance").innerText =
        info.ambulance || "--";
      document.getElementById("emerg-police").innerText = info.police || "--";
      document.getElementById("emerg-general").innerText = info.general || "--";
      document.getElementById("emerg-notes").innerText =
        info.notes || "Emergency contacts loaded.";

      const btn = document.getElementById("support-btn");
      if (btn)
        btn.href = `/support?city=${encodeURIComponent(
          city
        )}&country=${encodeURIComponent(country)}`;
    }
  } catch (e) {
    console.error("Support fetch failed", e);
  }
}

async function fetchAdvisory(env) {
  const healthDiv = document.getElementById("health-content");
  const sourcesContainer = document.getElementById("sources-container");
  const sourceNarrative = document.getElementById("source-narrative");

  try {
    const res = await fetch("/api/advisory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(env),
    });
    const data = await res.json();

    // Render Health Advice
    if (data.health_advice) {
      healthDiv.innerHTML = marked.parse(data.health_advice);
    } else {
      healthDiv.innerText = "Advice unavailable.";
    }

    // Render Sources
    if (data.sources) {
      sourcesContainer.innerHTML = "";
      data.sources.forEach((source) => {
        const badge = document.createElement("div");
        badge.className = "source-badge";
        // Simple icon mapping
        let icon = "🏭";
        const s = source.toLowerCase();
        if (s.includes("vehicle") || s.includes("traffic") || s.includes("car"))
          icon = "🚗";
        else if (
          s.includes("crop") ||
          s.includes("agriculture") ||
          s.includes("burn")
        )
          icon = "🌾";
        else if (s.includes("dust") || s.includes("construction")) icon = "🏗️";
        else if (s.includes("industry") || s.includes("factory")) icon = "🏭";
        else if (s.includes("fire") || s.includes("smoke")) icon = "🔥";

        badge.innerHTML = `<span>${icon}</span> ${source}`;
        sourcesContainer.appendChild(badge);
      });
      sourceNarrative.innerText = data.source_narrative || "";
    }

    // Render Planner (if returned by advisory)
    if (data.daily_plan && !data.daily_plan.error) {
      const plan = data.daily_plan;
      document.getElementById("mask-rec").innerText = plan.mask_level || "--";
      document.getElementById("hydration-rec").innerText = plan.hydration_ml
        ? plan.hydration_ml + " ml"
        : "--";

      const renderPlan = (id, txt) => {
        const el = document.getElementById(id);
        if (el)
          el.innerHTML = `<div class="planner-content">${marked.parse(
            txt
          )}</div>`;
      };
      renderPlan("plan-morning", plan.morning_plan);
      renderPlan("plan-afternoon", plan.afternoon_plan);
      renderPlan("plan-evening", plan.evening_plan);
    }
  } catch (e) {
    console.error("AI Advisory Error:", e);
    healthDiv.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 8px; color: #fca5a5;">
                <strong>⚠️ AI Unavailable</strong><br>
                <span style="font-size: 0.9rem;">${e.message}</span>
            </div>
        `;
  }
}

let aqiChartInstance = null;
let metricsChartInstance = null;
let radarChartInstance = null;

function updateCharts(env) {
  // AQI Gauge (Doughnut)
  const ctxAqi = document.getElementById("aqiChart").getContext("2d");

  let aqiColor = "#4ade80"; // Good
  if (env.aqi > 50) aqiColor = "#fbbf24"; // Moderate
  if (env.aqi > 100) aqiColor = "#fb923c"; // Unhealthy
  if (env.aqi > 150) aqiColor = "#ef4444"; // Hazardous

  const aqiData = {
    labels: ["AQI", "Remaining"],
    datasets: [
      {
        data: [env.aqi, 500 - env.aqi],
        backgroundColor: [aqiColor, "rgba(255, 255, 255, 0.1)"],
        borderWidth: 0,
        cutout: "85%",
        circumference: 180,
        rotation: 270,
      },
    ],
  };

  if (aqiChartInstance) {
    aqiChartInstance.data = aqiData;
    aqiChartInstance.update();
  } else {
    aqiChartInstance = new Chart(ctxAqi, {
      type: "doughnut",
      data: aqiData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
      },
    });
  }

  // Metrics Bar Chart
  const ctxMetrics = document.getElementById("metricsChart").getContext("2d");
  const metricsData = {
    labels: ["Temp (°C)", "Humidity (%)"],
    datasets: [
      {
        label: "Current Conditions",
        data: [env.temperature, env.humidity],
        backgroundColor: ["#667eea", "#764ba2"],
        borderRadius: 8,
        barThickness: 40,
      },
    ],
  };

  if (metricsChartInstance) {
    metricsChartInstance.data = metricsData;
    metricsChartInstance.update();
  } else {
    metricsChartInstance = new Chart(ctxMetrics, {
      type: "bar",
      data: metricsData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "rgba(255,255,255,0.1)" },
            ticks: { color: "#a0a0a0" },
          },
          x: { grid: { display: false }, ticks: { color: "#a0a0a0" } },
        },
        plugins: { legend: { display: false } },
      },
    });
  }

  // Radar Chart
  if (env.pollutants) {
    const ctxRadar = document.getElementById("radarChart").getContext("2d");
    const p = env.pollutants;
    const labels = ["PM2.5", "PM10", "NO2", "SO2", "O3"];
    const data = [
      p["PM2.5"]?.concentration || 0,
      p["PM10"]?.concentration || 0,
      p["NO2"]?.concentration || 0,
      p["SO2"]?.concentration || 0,
      p["O3"]?.concentration || 0,
    ];

    const radarData = {
      labels: labels,
      datasets: [
        {
          label: "Pollutant Concentration (µg/m³)",
          data: data,
          fill: true,
          backgroundColor: "rgba(102, 126, 234, 0.2)",
          borderColor: "#667eea",
          pointBackgroundColor: "#fff",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#667eea",
        },
      ],
    };

    if (radarChartInstance) {
      radarChartInstance.data = radarData;
      radarChartInstance.update();
    } else {
      radarChartInstance = new Chart(ctxRadar, {
        type: "radar",
        data: radarData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: { color: "rgba(255, 255, 255, 0.1)" },
              grid: { color: "rgba(255, 255, 255, 0.1)" },
              pointLabels: { color: "#fff", font: { size: 12 } },
              ticks: { display: false, backdropColor: "transparent" },
            },
          },
          plugins: { legend: { display: false } },
        },
      });
    }
  }
}

function updateDashboard(data) {
  const env = data.environment;
  let health = data.health_advice;

  // Update Charts
  updateCharts(env);

  // AQI Text
  const aqiVal = document.getElementById("aqi-value");
  aqiVal.innerText = env.aqi;

  // Color logic
  aqiVal.className = "card-value";
  let riskLevel = "Good";
  let riskIcon = "😊";

  if (env.aqi <= 50) {
    aqiVal.classList.add("aqi-good");
    riskLevel = "Good";
    riskIcon = "😊";
  } else if (env.aqi <= 100) {
    aqiVal.classList.add("aqi-moderate");
    riskLevel = "Moderate";
    riskIcon = "😐";
  } else if (env.aqi <= 150) {
    aqiVal.classList.add("aqi-unhealthy");
    riskLevel = "Unhealthy";
    riskIcon = "😷";
  } else {
    aqiVal.classList.add("aqi-hazardous");
    riskLevel = "Hazardous";
    riskIcon = "☠️";
  }

  document.getElementById("aqi-status").innerText = "Overall AQI";

  // Weather
  document.getElementById("temp-value").innerText = env.temperature + "°C";
  document.getElementById("weather-desc").innerText = env.description;
  document.getElementById("humidity-value").innerText = env.humidity + "%";

  // Weather Icon
  if (env.icon) {
    const iconImg = document.getElementById("weather-icon");
    iconImg.src = `https://openweathermap.org/img/wn/${env.icon}@2x.png`;
    iconImg.style.display = "block";
  }

  // Dominant Pollutant Logic
  let maxPol = "N/A";
  let maxVal = -1;
  if (env.pollutants) {
    const p = env.pollutants;
    // Check key pollutants
    ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"].forEach((key) => {
      if (p[key] && p[key].concentration > maxVal) {
        maxVal = p[key].concentration;
        maxPol = key;
      }
    });
  }
  document.getElementById("dom-pol-value").innerText = maxPol;

  // Risk Level
  document.getElementById("risk-value").innerText = riskLevel;
  document.getElementById("risk-icon").innerText = riskIcon;

  // Health Advice
  const healthDiv = document.getElementById("health-content");
  if (!health) {
    // Pending State
    healthDiv.innerHTML =
      '<span style="color: #94a3b8; font-style: italic;">Analyzing health impact...</span>';
  } else if (health.includes("Health advice unavailable")) {
    let errorDetail = "The AI health reasoning agent could not connect.";
    const match = health.match(/\(Error: (.*?)\)/);
    if (match && match[1]) errorDetail = match[1];

    healthDiv.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); padding: 1rem; border-radius: 8px; color: #fca5a5;">
                <strong>⚠️ AI Advice Unavailable</strong><br>
                <span style="font-size: 0.9rem; opacity: 0.9;">${errorDetail}</span>
            </div>
        `;
  } else {
    // Render Markdown using marked.js
    healthDiv.innerHTML = marked.parse(health);
  }

  // 5. Cigarette Equivalent & Source Analysis (New Features)
  if (data.cigarette_equivalent !== undefined) {
    const cigVal = document.getElementById("cig-value");
    if (cigVal) {
      cigVal.innerText = data.cigarette_equivalent;
      const cigCard = document.querySelector(".card-cigarette");
      if (cigCard) {
        if (data.cigarette_equivalent > 5) {
          cigCard.style.background =
            "linear-gradient(135deg, rgba(127, 29, 29, 0.4) 0%, rgba(69, 10, 10, 0.4) 100%)";
          cigVal.style.color = "#ff4d4d"; // Bright red
        } else if (data.cigarette_equivalent > 2) {
          cigCard.style.background =
            "linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(185, 28, 28, 0.1) 100%)";
          cigVal.style.color = "#fca5a5";
        } else {
          cigCard.style.background =
            "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)";
          cigVal.style.color = "#86efac";
        }
      }
    }
  }

  const sourceNarrative = document.getElementById("source-narrative");
  const sourcesContainer = document.getElementById("sources-container");

  if (sourceNarrative)
    sourceNarrative.innerText =
      data.source_narrative || "Analysis unavailable.";

  if (sourcesContainer && data.sources) {
    sourcesContainer.innerHTML = "";
    data.sources.forEach((source) => {
      const badge = document.createElement("div");
      badge.className = "source-badge";
      // Simple icon mapping
      let icon = "🏭";
      const s = source.toLowerCase();
      if (s.includes("vehicle") || s.includes("traffic") || s.includes("car"))
        icon = "🚗";
      else if (
        s.includes("crop") ||
        s.includes("agriculture") ||
        s.includes("burn")
      )
        icon = "🌾";
      else if (s.includes("dust") || s.includes("construction")) icon = "🏗️";
      else if (s.includes("industry") || s.includes("factory")) icon = "🏭";
      else if (s.includes("fire") || s.includes("smoke")) icon = "🔥";

      badge.innerHTML = `<span>${icon}</span> ${source}`;
      sourcesContainer.appendChild(badge);
    });
  }

  // Local News
  const newsContainer = document.getElementById("news-container");
  if (data.news && data.news.length > 0) {
    newsContainer.innerHTML = "";
    data.news.forEach((item) => {
      const div = document.createElement("div");
      div.className = "news-item";
      div.innerHTML = `
                <a href="${item.link}" target="_blank">${item.title}</a>
                <span class="news-source">${item.source} • ${item.date}</span>
            `;
      newsContainer.appendChild(div);
    });

    // Update Show More Button
    const showMoreBtn = document.getElementById("show-more-news");
    if (showMoreBtn) {
      const city = env.city || "India";
      showMoreBtn.href = `/news?city=${encodeURIComponent(city)}`;
      showMoreBtn.target = "_self"; // Open in same tab
    }
  } else {
    newsContainer.innerHTML =
      '<div style="color: rgba(255,255,255,0.5);">No recent news found for this location.</div>';
  }

  // Update Support Button with City
  const supportBtn = document.getElementById("support-btn");
  if (supportBtn) {
    const city = env.city || "India";
    const country = env.country || "";
    supportBtn.href = `/support?city=${encodeURIComponent(
      city
    )}&country=${encodeURIComponent(country)}`;
  }

  // Update Emergency Numbers
  if (data.emergency_info) {
    const em = data.emergency_info;
    document.getElementById("emerg-ambulance").innerText = em.ambulance || "--";
    document.getElementById("emerg-police").innerText = em.police || "--";
    document.getElementById("emerg-general").innerText = em.general || "--";
    document.getElementById("emerg-notes").innerText =
      em.notes || "Emergency contacts for this location.";
  }

  // Planner Agent
  if (data.daily_plan && !data.daily_plan.error) {
    const plan = data.daily_plan;
    document.getElementById("mask-rec").innerText = plan.mask_level || "--";
    document.getElementById("hydration-rec").innerText = plan.hydration_ml
      ? plan.hydration_ml + " ml"
      : "--";

    const renderPlannerSection = (id, content) => {
      const container = document.getElementById(id);
      if (!content) {
        container.innerHTML =
          '<div style="color: #94a3b8; font-style: italic;">No advice available</div>';
        return;
      }

      // Parse Markdown using marked.js
      container.innerHTML = `<div class="planner-content">${marked.parse(
        content
      )}</div>`;
    };

    renderPlannerSection("plan-morning", plan.morning_plan);
    renderPlannerSection("plan-afternoon", plan.afternoon_plan);
    renderPlannerSection("plan-evening", plan.evening_plan);
  } else if (data.daily_plan && data.daily_plan.error) {
    // Handle Planner Error
    document.getElementById("mask-rec").innerText = "Error";
    document.getElementById("hydration-rec").innerText = "--";
    ["plan-morning", "plan-afternoon", "plan-evening"].forEach((id) => {
      document.getElementById(
        id
      ).innerHTML = `<div style="color: #ef4444;">${data.daily_plan.error}</div>`;
    });
  }

  // Show Detected Location
  if (env.city) {
    document.getElementById(
      "detected-location"
    ).innerText = `📍 Detected Location: ${env.city}`;
  } else {
    document.getElementById("detected-location").innerText = "";
  }

  // Update Forecast & History
  if (data.forecast && data.history) {
    window.forecastData = data.forecast;
    window.historyData = data.history;
    window.forecastAnalysis = data.forecast_analysis;
    window.currentEnv = env; // Store for AI tools

    // Initial render (Forecast)
    toggleForecast();
  }
}

let mapInstance = null;
let forecastChartInstance = null;

function toggleForecast() {
  const isForecast = document.getElementById("forecast-toggle").checked;
  const data = isForecast ? window.forecastData : window.historyData;
  const analysis = isForecast
    ? window.forecastAnalysis
    : analyzeHistory(window.historyData);

  updateForecastChart(
    data,
    isForecast ? "Predicted AQI (Next 5 Days)" : "Historical AQI (Last 7 Days)"
  );

  // Update stats
  if (isForecast) {
    document.getElementById("worst-day").innerText = analysis.worst_day || "--";
    document.getElementById("worst-aqi-val").innerText = analysis.worst_aqi
      ? `AQI: ${analysis.worst_aqi}`
      : "";
    document.getElementById("best-day").innerText = analysis.best_day || "--";
    document.getElementById("best-aqi-val").innerText = analysis.best_aqi
      ? `AQI: ${analysis.best_aqi}`
      : "";
  } else {
    document.getElementById("worst-day").innerText = analysis.worst_day || "--";
    document.getElementById("worst-aqi-val").innerText = analysis.worst_aqi
      ? `AQI: ${analysis.worst_aqi}`
      : "";
    document.getElementById("best-day").innerText = analysis.best_day || "--";
    document.getElementById("best-aqi-val").innerText = analysis.best_aqi
      ? `AQI: ${analysis.best_aqi}`
      : "";
  }
}

// --- Helper Functions ---

function analyzeHistory(history) {
  if (!history || history.length === 0) return {};
  const maxItem = history.reduce((prev, current) =>
    prev.max_aqi > current.max_aqi ? prev : current
  );
  const minItem = history.reduce((prev, current) =>
    prev.max_aqi < current.max_aqi ? prev : current
  );
  return {
    worst_day: `${maxItem.day} (${maxItem.date})`,
    worst_aqi: maxItem.max_aqi,
    best_day: `${minItem.day} (${minItem.date})`,
    best_aqi: minItem.max_aqi,
  };
}

function updateForecastChart(forecastData, label) {
  const ctx = document.getElementById("forecastChart").getContext("2d");

  if (
    !forecastData ||
    !Array.isArray(forecastData) ||
    forecastData.length === 0
  ) {
    if (forecastChartInstance) {
      forecastChartInstance.destroy();
      forecastChartInstance = null;
    }
    // Optional: Draw "No Data" text
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.font = "14px Inter";
    ctx.fillStyle = "#94a3b8";
    ctx.textAlign = "center";
    ctx.fillText(
      "No data available",
      ctx.canvas.width / 2,
      ctx.canvas.height / 2
    );
    return;
  }

  // Format labels (Days)
  const labels = forecastData.map((item) => item.day);
  const dataPoints = forecastData.map((item) => item.max_aqi);

  // Determine color based on AQI
  const colors = dataPoints.map((aqi) => {
    if (aqi > 300) return "#ef4444";
    if (aqi > 200) return "#7e22ce";
    if (aqi > 150) return "#ef4444";
    if (aqi > 100) return "#f97316";
    if (aqi > 50) return "#eab308";
    return "#4ade80";
  });

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  forecastChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: label,
          data: dataPoints,
          backgroundColor: colors,
          borderRadius: 6,
          barThickness: 20,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: { color: "#cbd5e1" },
        },
        tooltip: {
          mode: "index",
          intersect: false,
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          titleColor: "#fff",
          bodyColor: "#cbd5e1",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8" },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" },
        },
      },
    },
  });
}

/* --- AI Tools Logic --- */

// 1. Vision (Snap & Check)
function triggerVision() {
  document.getElementById("vision-upload").click();
}

async function handleVisionUpload(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const formData = new FormData();
    formData.append("image", file);

    // Add context
    if (window.currentEnv) {
      formData.append("aqi", window.currentEnv.aqi);
      formData.append("city", window.currentEnv.city);
    }

    // Show simplified loading
    alert("Analyzing image... please wait.");

    try {
      const response = await fetch("/api/ai/vision", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.result) {
        alert("Vision Analysis:\n\n" + data.result);
      } else {
        alert("Analysis failed.");
      }
    } catch (e) {
      alert("Error uploading image: " + e);
    }

    // Reset input
    input.value = "";
  }
}

// 2. Chat (Ask BreatheAI)
function toggleChat() {
  const win = document.getElementById("chat-window");
  win.classList.toggle("hidden");
  if (!win.classList.contains("hidden")) {
    document.getElementById("chat-input-field").focus();
  }
}

async function sendChat() {
  const input = document.getElementById("chat-input-field");
  const query = input.value.trim();
  if (!query) return;

  // Append User Msg
  appendMessage(query, "user");
  input.value = "";

  // Context
  const context = window.currentEnv || { city: "Unknown", aqi: "Unknown" };

  try {
    const response = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, env: context }),
    });
    const data = await response.json();

    if (data.result) {
      // Simple markdown parsing for chat
      let cleanText = data.result.replace(/\*\*(.*?)\*\*/g, "<b></b>");
      appendMessage(cleanText, "bot");
    } else {
      appendMessage("Sorry, I'm offline right now.", "bot");
    }
  } catch (e) {
    appendMessage("Error connecting to AI.", "bot");
  }
}

function appendMessage(text, sender) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.innerHTML = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// 3. Commute Optimizer
async function triggerCommute() {
  const resultDiv = document.getElementById("commute-result");
  resultDiv.style.display = "block";
  resultDiv.innerText = "Thinking...";

  if (!window.currentEnv) {
    resultDiv.innerText = "No location data.";
    return;
  }

  try {
    const lat = window.currentEnv.lat || 0;
    const lon = window.currentEnv.lon || 0;
    const aqi = window.currentEnv.aqi || 0;

    const response = await fetch(
      `/api/ai/commute?lat=${lat}&lon=${lon}&aqi=${aqi}`
    );
    const data = await response.json();
    resultDiv.innerHTML = data.result || "No advice found.";
  } catch (e) {
    resultDiv.innerText = "Error fetching advice.";
  }
}

// 4. Time Machine
async function triggerHistory() {
  const resultDiv = document.getElementById("history-result");
  resultDiv.style.display = "block";
  resultDiv.innerText = "Checking archives...";

  if (!window.currentEnv) {
    resultDiv.innerText = "No location data.";
    return;
  }

  try {
    const lat = window.currentEnv.lat || 0;
    const lon = window.currentEnv.lon || 0;
    const aqi = window.currentEnv.aqi || 0;

    const response = await fetch(
      `/api/ai/history?lat=${lat}&lon=${lon}&aqi=${aqi}`
    );
    const data = await response.json();
    resultDiv.innerHTML = data.result || "No history found.";
  } catch (e) {
    resultDiv.innerText = "Error fetching history.";
  }
}
