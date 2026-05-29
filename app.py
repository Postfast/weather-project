import streamlit as st
import pandas as pd
import requests

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="SkyCast Pro", layout="wide")

# 2. CSS STYLING (Optimized for Mobile/Dark Mode)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #87CEEB 0%, #E0F7FA 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #87CEEB 20%, #E0F7FA 100%); }
    [data-testid="stMetric"] { 
        background-color: rgba(255, 255, 255, 0.6); 
        padding: 15px; 
        border-radius: 15px; 
        color: #333; 
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA CACHING (Updates every 1 hour / 3600 seconds)
@st.cache_data(ttl=3600)
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,windspeed_10m,pressure_msl&forecast_days=1"
    response = requests.get(url).json()
    return response

# 4. DATA SETUP
cities_data = {
    "Nairobi": (-1.2921, 36.8219), "Nakuru": (-0.3031, 36.0800),
    "Naivasha": (-0.7173, 36.4313), "Kisumu": (-0.1022, 34.7617),
    "Eldoret": (0.5143, 35.2698), "Lodwar": (3.1192, 35.5975),
    "Uasin Gishu": (0.5500, 35.2833), "Turkana": (3.0000, 36.0000),
    "Mombasa": (-4.0435, 39.6682), "Malindi": (-3.2200, 40.1167),
    "Kilifi": (-3.6305, 39.8499), "Kakamega": (0.2827, 34.7519),
    "Machakos": (-1.5200, 37.2667), "Samburu": (1.0000, 37.0000)
}

units_map = {"Temperature": "°C", "Humidity": "%", "Wind Speed": " km/h", "Pressure": " hPa"}

# 5. SIDEBAR
st.sidebar.title("☁️ SkyCast Pro")
city = st.sidebar.selectbox("Station", list(cities_data.keys()))
unit_toggle = st.sidebar.radio("Temp Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
metrics = st.sidebar.multiselect("Metrics", list(units_map.keys()), default=["Temperature", "Humidity"])

# 6. DATA FETCHING & LOGIC
lat, lon = cities_data[city]
response = get_weather_data(lat, lon)
df = pd.DataFrame(response['hourly'])
df['time'] = pd.to_datetime(df['time'])

if unit_toggle == "Fahrenheit (°F)":
    df['temperature_2m'] = (df['temperature_2m'] * 9/5) + 32
    units_map["Temperature"] = "°F"
else:
    units_map["Temperature"] = "°C"

# 7. LAYOUT
st.title(f"🌤️ {city} Analytical Dashboard")
cols = st.columns(len(metrics) if metrics else 1)

mapping = {"Temperature": "temperature_2m", "Humidity": "relative_humidity_2m", 
           "Wind Speed": "windspeed_10m", "Pressure": "pressure_msl"}

for i, metric in enumerate(metrics):
    col_name = mapping[metric]
    val = df[col_name][0]
    unit_label = units_map[metric]
    
    with cols[i] if len(metrics) > 0 else st:
        st.metric(metric, f"{val:.1f}{unit_label}")
        # Fast native line chart
        st.line_chart(df.set_index('time')[[col_name]], height=200)