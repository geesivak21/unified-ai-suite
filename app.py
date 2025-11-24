import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Unified AI Apps", layout="wide")

# App titles + URLs
APPS = {
    "AI Utility Suite": "https://ai-utility-suite.streamlit.app",
    "Procurement AI Dashboard": "https://procurement-ai-dashboard.streamlit.app",
}

# Add ?embed=true for smooth iframe rendering
APPS_EMBED = {
    name: url + "?embed=true"
    for name, url in APPS.items()
}

# Sidebar navigation
st.sidebar.title("Applications")
selected_app = st.sidebar.radio("Choose an application:", list(APPS.keys()))

# Show selected app
st.title(selected_app)

# Fullscreen link
st.markdown(f"[Open Fullscreen]({APPS[selected_app]})")

# Preview inside iframe
components.iframe(APPS_EMBED[selected_app], height=1400)
