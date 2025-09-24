import os
import joblib
import numpy as np
import streamlit as st
import pandas as pd

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="Bus Ridership Prediction",
    layout="wide"
)

# ------------------------
# Load Model
# ------------------------
MODEL_PATH = "model/rf_best_model.pkl"

@st.cache_resource
def load_model(path):
    return joblib.load(path)

rf_best = load_model(MODEL_PATH)

# ------------------------
# UI Inputs
# ------------------------
st.title("🚌 Bus Ridership Prediction")

with st.form(key="prediction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        month = st.number_input("Month", min_value=1, max_value=12, value=5)
        day = st.number_input("Day", min_value=1, max_value=31, value=5)
        hour = st.number_input("Hour", min_value=0, max_value=23, value=12)

    with col2:
        borough = st.selectbox("Borough", ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"])
        day_of_week = st.number_input("Day of Week (0=Mon, 6=Sun)", min_value=0, max_value=6, value=0)
        is_weekend = st.selectbox("Is Weekend?", [0, 1])

    submitted = st.form_submit_button("Predict Ridership")

# ------------------------
# Prediction
# ------------------------
def predict_ridership(month, day, hour, borough, day_of_week, is_weekend):
    borough_columns = ["borough_Bronx", "borough_Brooklyn", "borough_Manhattan", "borough_Queens", "borough_Staten Island"]
    borough_data = [0] * len(borough_columns)

    # Set borough one-hot encoding
    if borough in borough_columns:
        borough_index = borough_columns.index(f"borough_{borough}")
        borough_data[borough_index] = 1

    input_data = np.array([[month, day, hour, is_weekend, day_of_week] + borough_data])
    return rf_best.predict(input_data)[0]

# ------------------------
# Display Prediction
# ------------------------
if submitted:
    prediction = predict_ridership(month, day, hour, borough, day_of_week, is_weekend)
    st.subheader("Prediction Result")
    st.write(f"📅 **Date:** Month {month}, Day {day}, Hour {hour}")
    st.write(f"📍 **Borough:** {borough}")
    st.write(f"📊 **Predicted Ridership:** {round(prediction, 2)} riders")
