import requests
import streamlit as st

API_URL = "https://soil-ia40.onrender.com/predict"

SOIL_TYPES = ["Black", "Clayey", "Loamy", "Red", "Sandy"]
CROP_TYPES = [
    "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
    "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat",
]

st.set_page_config(page_title="Fertilizer Recommender", page_icon="🌾")
st.title("🌾 Fertilizer Recommendation")

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        temperature = st.number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=26.0)
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=52.0)
        moisture = st.number_input("Moisture (%)", min_value=0.0, max_value=100.0, value=38.0)
        nitrogen = st.number_input("Nitrogen", min_value=0.0, max_value=200.0, value=37.0)

    with col2:
        potassium = st.number_input("Potassium", min_value=0.0, max_value=200.0, value=0.0)
        phosphorous = st.number_input("Phosphorous", min_value=0.0, max_value=200.0, value=0.0)
        soil_type = st.selectbox("Soil Type", SOIL_TYPES)
        crop_type = st.selectbox("Crop Type", CROP_TYPES)

    submitted = st.form_submit_button("Predict Fertilizer")

if submitted:
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "moisture": moisture,
        "nitrogen": nitrogen,
        "potassium": potassium,
        "phosphorous": phosphorous,
        "soil_type": soil_type,
        "crop_type": crop_type,
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        fertilizer = response.json()["fertilizer"]
        st.success(f"Recommended Fertilizer: **{fertilizer}**")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        st.error(f"Something went wrong: {e}")
