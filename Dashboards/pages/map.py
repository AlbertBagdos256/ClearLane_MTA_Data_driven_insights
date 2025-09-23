import os
import streamlit as st
import pandas as pd

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="🗺️ Interactive Map of Bus Violations",
    layout="wide"
)


def load_map() -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Dashboards/
    data_dir = os.path.join(base_dir, "data")
    map_file = os.path.join(data_dir, "bus_map.html")

    if not os.path.exists(map_file):
        return None

    with open(map_file, "r", encoding="utf-8") as f:
        return f.read()

# ------------------------
# Load Prebuilt Map
# ------------------------
map_html = load_map()

if map_html:
    st.markdown("### Interactive map")
    st.components.v1.html(map_html, height=800, scrolling=True)
else:
    st.error("❌ Map file not found. Please generate `bus_map.html` first.")
