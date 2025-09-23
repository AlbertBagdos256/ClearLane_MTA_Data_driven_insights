import os
import streamlit as st

# ------------------------
# Page Config
# ------------------------
st.set_page_config(
    page_title="🗺️ Interactive Map of Bus Violations",
    layout="wide"
)

# ------------------------
# Load Prebuilt Map
# ------------------------
map_file = "data/bus_map.html"

if os.path.exists(map_file):
    with open(map_file, "r", encoding="utf-8") as f:
        map_html = f.read()

    # Display the HTML map
    st.components.v1.html(map_html, height=800, scrolling=True)
else:
    st.error("Map file not found. Please generate bus_map.html first.")
