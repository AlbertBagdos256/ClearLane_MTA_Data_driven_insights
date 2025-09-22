import streamlit as st
import os
st.set_page_config(
    page_title="NYC Bus Violations",
    page_icon="🚍",
    layout="wide"
)




st.title("🚍 NYC Bus Violations Dashboard")

st.markdown("""
Welcome to the **NYC Bus Violations Analytics Dashboard**.  
Navigate using the sidebar to explore:
- **Overview** (summary KPIs & top hotspots)
- **Hotspots Map** (interactive map with routes and violations)
- **Time Patterns** (violations by hour/day/month)
""")
