// Load countries on start
window.onload = async function() {
    try {
        const response = await fetch('https://restcountries.com/v3.1/all?fields=name,cca2');
        const data = await response.json();
        
        const select = document.getElementById('country-select');
        select.innerHTML = '<option value="">Country</option>';
        
        data.sort((a, b) => a.name.common.localeCompare(b.name.common));
        
        data.forEach(country => {
            const option = document.createElement('option');
            option.value = country.cca2;
            option.text = country.name.common;
            select.appendChild(option);
        });
    } catch (e) {
        console.error("Failed to load countries", e);
        document.getElementById('country-select').innerHTML = '<option value="">Error</option>';
    }
};

function getLocation() {
    showLoading();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(fetchData, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
        hideLoading();
    }
}

async function searchLocation() {
    const city = document.getElementById('city-input').value;
    const country = document.getElementById('country-select').value;
    const resultsDiv = document.getElementById('search-results');

    if (!city) {
        alert("Please enter a city name");
        return;
    }

    resultsDiv.style.display = 'none';
    showLoading();
    
    try {
        const response = await fetch(`/api/geocode?city=${encodeURIComponent(city)}&country=${country}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server Error ${response.status}: ${errorText.substring(0, 100)}`);
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
            alert(data.error);
            return;
        }

        if (data.length === 0) {
            alert("No locations found.");
            return;
        }

        if (data.length === 1) {
            selectLocation(data[0]);
        } else {
            resultsDiv.innerHTML = '';
            data.forEach(loc => {
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerText = `${loc.name}, ${loc.state ? loc.state + ', ' : ''}${loc.country}`;
                div.onclick = () => selectLocation(loc);
                resultsDiv.appendChild(div);
            });
            resultsDiv.style.display = 'flex';
        }

    } catch (e) {
        alert("Search Error: " + e);
        hideLoading();
    }
}

function selectLocation(loc) {
    document.getElementById('search-results').style.display = 'none';
    const position = {
        coords: {
            latitude: loc.lat,
            longitude: loc.lon
        }
    };
    fetchData(position);
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(error) {
    alert("Error getting location: " + error.message);
    hideLoading();
}

async function fetchData(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    showLoading();

    try {
        const response = await fetch(`/api/environment/${lat}/${lon}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server Error ${response.status}: ${errorText.substring(0, 100)}`);
        }

        let data;
        const text = await response.text();
        try {
            data = JSON.parse(text);
        } catch (e) {
            throw new Error(`Invalid JSON response: ${text.substring(0, 100)}...`);
        }

        if (data.error) {
            alert("API Error: " + data.error);
            return;
        }

        updateDashboard(data);
    } catch (e) {
        alert("Network Error: " + e);
    } finally {
        hideLoading();
        document.getElementById('dashboard').style.display = 'grid';
    }
}

let aqiChartInstance = null;
let metricsChartInstance = null;
let radarChartInstance = null;

function updateCharts(env) {
    // AQI Gauge (Doughnut)
    const ctxAqi = document.getElementById('aqiChart').getContext('2d');
    
    let aqiColor = '#4ade80'; // Good
    if (env.aqi > 50) aqiColor = '#fbbf24'; // Moderate
    if (env.aqi > 100) aqiColor = '#fb923c'; // Unhealthy
    if (env.aqi > 150) aqiColor = '#ef4444'; // Hazardous

    const aqiData = {
        labels: ['AQI', 'Remaining'],
        datasets: [{
            data: [env.aqi, 500 - env.aqi],
            backgroundColor: [aqiColor, 'rgba(255, 255, 255, 0.1)'],
            borderWidth: 0,
            cutout: '85%',
            circumference: 180,
            rotation: 270
        }]
    };

    if (aqiChartInstance) {
        aqiChartInstance.data = aqiData;
        aqiChartInstance.update();
    } else {
        aqiChartInstance = new Chart(ctxAqi, {
            type: 'doughnut',
            data: aqiData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } }
            }
        });
    }

    // Metrics Bar Chart
    const ctxMetrics = document.getElementById('metricsChart').getContext('2d');
    const metricsData = {
        labels: ['Temp (°C)', 'Humidity (%)'],
        datasets: [{
            label: 'Current Conditions',
            data: [env.temperature, env.humidity],
            backgroundColor: ['#667eea', '#764ba2'],
            borderRadius: 8,
            barThickness: 40
        }]
    };

    if (metricsChartInstance) {
        metricsChartInstance.data = metricsData;
        metricsChartInstance.update();
    } else {
        metricsChartInstance = new Chart(ctxMetrics, {
            type: 'bar',
            data: metricsData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } },
                    x: { grid: { display: false }, ticks: { color: '#a0a0a0' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // Radar Chart
    if (env.pollutants) {
        const ctxRadar = document.getElementById('radarChart').getContext('2d');
        const p = env.pollutants;
        const labels = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3'];
        const data = [
            p['PM2.5']?.concentration || 0,
            p['PM10']?.concentration || 0,
            p['NO2']?.concentration || 0,
            p['SO2']?.concentration || 0,
            p['O3']?.concentration || 0
        ];

        const radarData = {
            labels: labels,
            datasets: [{
                label: 'Pollutant Concentration (µg/m³)',
                data: data,
                fill: true,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: '#667eea',
                pointBackgroundColor: '#fff',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea'
            }]
        };

        if (radarChartInstance) {
            radarChartInstance.data = radarData;
            radarChartInstance.update();
        } else {
            radarChartInstance = new Chart(ctxRadar, {
                type: 'radar',
                data: radarData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: '#fff', font: { size: 12 } },
                            ticks: { display: false, backdropColor: 'transparent' }
                        }
                    },
                    plugins: { legend: { display: false } }
                }
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
    const aqiVal = document.getElementById('aqi-value');
    aqiVal.innerText = env.aqi;
    
    // Color logic
    aqiVal.className = 'card-value';
    let riskLevel = "Good";
    let riskIcon = "😊";
    
    if(env.aqi <= 50) {
        aqiVal.classList.add('aqi-good');
        riskLevel = "Good";
        riskIcon = "😊";
    } else if(env.aqi <= 100) {
        aqiVal.classList.add('aqi-moderate');
        riskLevel = "Moderate";
        riskIcon = "😐";
    } else if(env.aqi <= 150) {
        aqiVal.classList.add('aqi-unhealthy');
        riskLevel = "Unhealthy";
        riskIcon = "😷";
    } else {
        aqiVal.classList.add('aqi-hazardous');
        riskLevel = "Hazardous";
        riskIcon = "☠️";
    }

    document.getElementById('aqi-status').innerText = "Overall AQI";

    // Weather
    document.getElementById('temp-value').innerText = env.temperature + "°C";
    document.getElementById('weather-desc').innerText = env.description;
    document.getElementById('humidity-value').innerText = env.humidity + "%";

    // Weather Icon
    if (env.icon) {
        const iconImg = document.getElementById('weather-icon');
        iconImg.src = `https://openweathermap.org/img/wn/${env.icon}@2x.png`;
        iconImg.style.display = 'block';
    }

    // Dominant Pollutant Logic
    let maxPol = "N/A";
    let maxVal = -1;
    if (env.pollutants) {
        const p = env.pollutants;
        // Check key pollutants
        ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3', 'CO'].forEach(key => {
            if (p[key] && p[key].concentration > maxVal) {
                maxVal = p[key].concentration;
                maxPol = key;
            }
        });
    }
    document.getElementById('dom-pol-value').innerText = maxPol;

    // Risk Level
    document.getElementById('risk-value').innerText = riskLevel;
    document.getElementById('risk-icon').innerText = riskIcon;

    // Health Advice
    const healthDiv = document.getElementById('health-content');
    if (health.includes("Health advice unavailable")) {
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
        // Render Markdown-ish
        // 1. Headers
        let html = health.replace(/### (.*?)\n/g, '<h3>$1</h3>');
        // 2. Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // 3. Newlines
        html = html.replace(/\n/g, '<br>');
        
        healthDiv.innerHTML = html;
    }

    // Planner Agent
    if (data.daily_plan) {
        const plan = data.daily_plan;
        document.getElementById('mask-rec').innerText = plan.mask_level;
        document.getElementById('hydration-rec').innerText = plan.hydration_ml + " ml";

        const renderList = (id, items) => {
            const ul = document.getElementById(id);
            ul.innerHTML = items.map(item => {
                // Parse Markdown Bold
                const formattedItem = item.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                return `<li>${formattedItem}</li>`;
            }).join('');
        };

        renderList('plan-morning', plan.morning_plan);
        renderList('plan-afternoon', plan.afternoon_plan);
        renderList('plan-evening', plan.evening_plan);
    }
    
    // Update Map
    if (data.micro_aqi) {
        const centerLat = data.micro_aqi[0].lat;
        const centerLon = data.micro_aqi[0].lon;
        updateMap(centerLat, centerLon, data.micro_aqi);
    }
    
    // Show Detected Location
    if (env.city) {
        document.getElementById('detected-location').innerText = `📍 Detected Location: ${env.city}`;
    } else {
        document.getElementById('detected-location').innerText = "";
    }
}

let mapInstance = null;

function updateMap(lat, lon, microData) {
    // Ensure the map container is visible before initializing
    const mapContainer = document.getElementById('map');
    
    if (!mapInstance) {
        mapInstance = L.map('map').setView([lat, lon], 13);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(mapInstance);
    } else {
        mapInstance.setView([lat, lon], 13);
        mapInstance.eachLayer((layer) => {
            if (layer instanceof L.Marker || layer instanceof L.CircleMarker) {
                mapInstance.removeLayer(layer);
            }
        });
    }

    // Fix for map not rendering correctly in hidden container
    setTimeout(() => {
        mapInstance.invalidateSize();
    }, 100);

    // Add User Location Marker
    L.marker([lat, lon]).addTo(mapInstance)
        .bindPopup("<b>You are here</b><br>Center of Analysis")
        .openPopup();

    // Add Micro-Zone Markers
    microData.forEach(zone => {
        let color = '#4ade80'; // Good (Green)
        let fillColor = '#4ade80';
        
        // Standard AQI Color Scale
        if (zone.aqi > 300) {
            color = '#7f1d1d'; // Hazardous (Maroon)
            fillColor = '#991b1b';
        } else if (zone.aqi > 200) {
            color = '#7e22ce'; // Very Unhealthy (Purple)
            fillColor = '#a855f7';
        } else if (zone.aqi > 150) {
            color = '#ef4444'; // Unhealthy (Red)
            fillColor = '#f87171';
        } else if (zone.aqi > 100) {
            color = '#f97316'; // Unhealthy for Sensitive (Orange)
            fillColor = '#fb923c';
        } else if (zone.aqi > 50) {
            color = '#eab308'; // Moderate (Yellow)
            fillColor = '#facc15';
        }

        L.circleMarker([zone.lat, zone.lon], {
            radius: 12, // Increased size
            fillColor: fillColor,
            color: "#ffffff", // White border
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(mapInstance)
        .bindPopup(`
            <div style="text-align: center;">
                <strong style="font-size: 1.1em; color: ${color}">${zone.type}</strong><br>
                <span style="font-size: 1.2em; font-weight: bold;">AQI: ${zone.aqi}</span><br>
                <span style="color: #666;">Risk: ${zone.risk}</span>
            </div>
        `);
    });
}
