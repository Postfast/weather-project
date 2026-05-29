import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="SkyCast Pro", layout="wide")

# 2. CSS STYLING (Forced Dark Text & Clean Mobile Layout)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #87CEEB 0%, #E0F7FA 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #87CEEB 20%, #E0F7FA 100%); }
    
    /* Metrics and Chart containers */
    [data-testid="stMetric"], .stPlotlyChart { 
        background-color: rgba(255, 255, 255, 0.7); 
        padding: 15px; 
        border-radius: 15px; 
    }
    
    /* Force text to be black regardless of dark mode */
    [data-testid="stMetric"] div, [data-testid="stMetric"] label, .stPlotlyChart {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CACHED DATA FETCHING
@st.cache_data(ttl=3600)
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,windspeed_10m,pressure_msl&forecast_days=1"
    return requests.get(url).json()

# 4. CONFIGURATION
cities_data = {
    "Nairobi": (-1.2921, 36.8219), "Nakuru": (-0.3031, 36.0800),
    "Naivasha": (-0.7173, 36.4313), "Kisumu": (-0.1022, 34.7617),
    "Eldoret": (0.5143, 35.2698), "Lodwar": (3.1192, 35.5975),
    "Mombasa": (-4.0435, 39.6682), "Malindi": (-3.2200, 40.1167)
}
units_map = {"Temperature": "°C", "Humidity": "%", "Wind Speed": " km/h", "Pressure": " hPa"}

# 5. SIDEBAR
st.sidebar.title("☁️ SkyCast Pro")
city = st.sidebar.selectbox("Station", list(cities_data.keys()))
unit_toggle = st.sidebar.radio("Temp Unit", ["Celsius (°C)", "Fahrenheit (°F)"])
metrics = st.sidebar.multiselect("Metrics", list(units_map.keys()), default=["Temperature", "Humidity"])

# 6. DATA PROCESSING
lat, lon = cities_data[city]
response = get_weather_data(lat, lon)
df = pd.DataFrame(response['hourly'])
df['time'] = pd.to_datetime(df['time'])

if unit_toggle == "Fahrenheit (°F)":
    df['temperature_2m'] = (df['temperature_2m'] * 9/5) + 32
    units_map["Temperature"] = "°F"

# 7. RESPONSIVE LAYOUT
st.title(f"🌤️ {city} Analytical Dashboard")
mapping = {"Temperature": "temperature_2m", "Humidity": "relative_humidity_2m", 
           "Wind Speed": "windspeed_10m", "Pressure": "pressure_msl"}

for metric in metrics:
    with st.container():
        col_name = mapping[metric]
        val = df[col_name][0]
        unit_label = units_map[metric]
        
        st.metric(metric, f"{val:.1f}{unit_label}")
        
        # Static chart configuration (no zoom/toolbar)
        config = {'displayModeBar': False, 'staticPlot': True}
        fig = px.line(df, x='time', y=col_name)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                          height=200, margin=dict(l=0, r=0, t=10, b=0),
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='gray'))
        
        st.plotly_chart(fig, use_container_width=True, config=config)
        st.divider()