import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Rainfall Prediction Pro",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6; /* Fallback background */
    }
    /* New dark blue gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
    }
    .st-emotion-cache-1y4p8pa {
        width: 100%;
        padding: 1rem 0;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
        font-family: 'sans-serif';
    }
    .stButton>button {
        background-color: #ffffff;
        color: #2c5364;
        border-radius: 50px;
        border: 1px solid #2c5364;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2c5364;
        color: white;
        border: 1px solid white;
    }
    .prediction-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    .info-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    /* Style sidebar */
    .st-emotion-cache-10oheav {
        background-color: rgba(0, 0, 0, 0.2);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    .st-emotion-cache-1v0mbdj { /* Sidebar header color */
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


# --- Initialize Session State for Sliders ---
if 'pressure' not in st.session_state:
    st.session_state.pressure = 1015.0
    st.session_state.dewpoint = 12.0
    st.session_state.humidity = 65
    st.session_state.cloud = 4
    st.session_state.sunshine = 7.6
    st.session_state.winddirection = 180
    st.session_state.windspeed = 20

# --- Preset Data Functions ---
def load_rainy_day():
    st.session_state.pressure = 995.0
    st.session_state.dewpoint = 20.0
    st.session_state.humidity = 95
    st.session_state.cloud = 8
    st.session_state.sunshine = 0.5
    st.session_state.winddirection = 210
    st.session_state.windspeed = 55

def load_dry_day():
    st.session_state.pressure = 1025.0
    st.session_state.dewpoint = 5.0
    st.session_state.humidity = 40
    st.session_state.cloud = 1
    st.session_state.sunshine = 12.0
    st.session_state.winddirection = 150
    st.session_state.windspeed = 10

# --- Sidebar for User Input ---
with st.sidebar:
    st.header("🌦️ Enter Weather Data")

    st.subheader("Load Presets")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Rainy Day", on_click=load_rainy_day, use_container_width=True)
    with col2:
        st.button("Dry Day", on_click=load_dry_day, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Atmospheric Features")
    pressure = st.slider('Pressure (hPa)', 950.0, 1050.0, key='pressure', step=0.1, help="Atmospheric pressure at sea level")
    dewpoint = st.slider('Dew Point (°C)', -20.0, 40.0, key='dewpoint', step=0.1)
    humidity = st.slider('Humidity (%)', 0, 100, key='humidity')
    
    st.subheader("Sky & Sun")
    cloud = st.slider('Cloud Cover (oktas)', 0, 8, key='cloud', help="Cloudiness measured in eighths of the sky")
    sunshine = st.slider('Sunshine (hours)', 0.0, 15.0, key='sunshine', step=0.1)
    
    st.subheader("Wind Features")
    winddirection = st.slider('Wind Direction (degrees)', 0, 360, key='winddirection')
    windspeed = st.slider('Wind Speed (km/h)', 0, 150, key='windspeed')
    
    st.markdown("---")
    st.header("About This App")
    st.info(
        "This application uses a Random Forest model to predict if it will rain tomorrow based on today's weather. Adjust the sliders to see the forecast change!"
    )

# --- Main Page ---
st.title("🌌 Rainfall Prediction Pro")
st.markdown("### An interactive app to forecast tomorrow's weather.")
st.markdown("---")

# This order must exactly match the training order of your model
data = {
    'pressure': st.session_state.pressure, 'dewpoint': st.session_state.dewpoint, 'humidity': st.session_state.humidity, 'cloud': st.session_state.cloud, 
    'sunshine': st.session_state.sunshine, 'winddirection': st.session_state.winddirection, 'windspeed': st.session_state.windspeed
}
expected_columns = list(data.keys())
input_df = pd.DataFrame(data, index=[0])[expected_columns]

# --- Main Layout ---
col1, col2 = st.columns([2, 1.5])

with col1:
    st.subheader("Prediction Outcome")
    
    # Prediction button and logic
    if st.button('Predict Rainfall for Tomorrow', use_container_width=True):
        try:
            with open('rainfall_prediction_model.pkl', 'rb') as file:
                loaded_object = pickle.load(file)
            model = loaded_object.get('model') if isinstance(loaded_object, dict) else loaded_object

            if model is None:
                 st.error("Could not load the model from the .pkl file.")
            else:
                prediction = model.predict(input_df)
                with st.container():
                    st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
                    if prediction[0] == 1:
                        st.markdown('<h1>☔<br>It will likely rain!</h1>', unsafe_allow_html=True)
                        st.info("💡 Suggestion: Don't forget to carry an umbrella!")
                    else:
                        st.markdown('<h1>☀️<br>It will likely be dry!</h1>', unsafe_allow_html=True)
                        st.info("💡 Suggestion: A great day for outdoor activities!")
                    st.markdown('</div>', unsafe_allow_html=True)

        except FileNotFoundError:
            st.error("Model file not found. Ensure 'rainfall_prediction_model.pkl' is present.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Adjust the sliders in the sidebar and click the button to see the prediction.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Additional Features Section ---
    st.subheader("Learn More & See Future Outlook")
    tab1, tab2 = st.tabs(["Feature Explanations", "Illustrative 5-Day Forecast"])

    with tab1:
        st.markdown("#### Understanding the Weather Metrics")
        st.markdown("- **Pressure (hPa):** Hectopascals, a unit for measuring atmospheric pressure. High pressure is often associated with clear skies, while low pressure can indicate stormy weather.")
        st.markdown("- **Dew Point (°C):** The temperature to which air must be cooled to become saturated with water vapor. A higher dew point means more moisture in the air.")
        st.markdown("- **Cloud Cover (oktas):** A scale from 0 to 8 measuring what fraction of the sky is covered in clouds. 0 is a clear sky, 8 is completely overcast.")
        st.markdown("---")
        st.markdown("#### When is Rain Likely?")
        st.markdown(
            "Rain isn't caused by a single factor, but rather a combination of conditions. "
            "The likelihood of rain increases significantly when you observe the following:"
        )
        st.markdown("- **Low Atmospheric Pressure:** When pressure is low (e.g., below 1000 hPa), air rises, cools, and moisture condenses to form rain.")
        st.markdown("- **High Humidity & Dew Point:** High humidity (> 85%) means the air is saturated. When the dew point is close to the air temperature, rain is more probable.")
        st.markdown("- **High Cloud Cover & Low Sunshine:** A mostly overcast sky (7-8 oktas) with little sunshine indicates conditions are ripe for precipitation.")
        st.markdown("Try using the **'Load Rainy Day'** preset to see a typical combination of these factors.")

    with tab2:
        st.markdown("#### Example 5-Day Outlook")
        st.caption("This is an illustrative forecast and is not based on a predictive model.")
        forecast_cols = st.columns(5)
        today = datetime.now()
        for i in range(5):
            day = today + timedelta(days=i + 1)
            with forecast_cols[i]:
                st.markdown(f"<div style='text-align: center; padding: 10px; background-color: rgba(255,255,255,0.1); border-radius: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"**{day.strftime('%a')}**")
                if np.random.rand() > 0.5:
                    st.markdown("<h2 style='font-size: 2.5em;'>☀️</h2>", unsafe_allow_html=True)
                    temp = f"{np.random.randint(int(st.session_state.dewpoint)+5, int(st.session_state.dewpoint)+15)}°C"
                else:
                    st.markdown("<h2 style='font-size: 2.5em;'>🌧️</h2>", unsafe_allow_html=True)
                    temp = f"{np.random.randint(int(st.session_state.dewpoint), int(st.session_state.dewpoint)+10)}°C"
                st.write(temp)
                st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("Current Weather Inputs")
    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        # Data Table
        st.markdown("##### Input Values")
        st.dataframe(input_df.T.rename(columns={0: 'Values'}), use_container_width=True)
        
        # Radar Chart
        st.markdown("##### Weather Factors Visualization")
        categories = [col.replace('_', ' ').title() for col in expected_columns]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
              r=input_df.iloc[0].values,
              theta=categories,
              fill='toself',
              name='Input Values'
        ))
        fig.update_layout(
          polar=dict(radialaxis=dict(visible=True, range=[0, 100])), # Normalized-like range for better visuals
          showlegend=False,
          paper_bgcolor='rgba(0,0,0,0)',
          plot_bgcolor='rgba(0,0,0,0)',
          font_color='white',
          margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #a9a9a9;'>Made with Streamlit | Kharagpur, West Bengal</div>", unsafe_allow_html=True)

