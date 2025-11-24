# Import the necessary libraries
import os

# Try to load from Streamlit Cloud secrets first
try:
    import streamlit as st

    if hasattr(st, "secrets") and "OPENAI_API_KEY_SUMMARIZE" in st.secrets:
        # --- Load from Streamlit Cloud secrets ---
        azure_openai_api_key = st.secrets["AZUREOPENAI_API_KEY"]
        azure_api_version = st.secrets["AZUREOPENAI_API_VERSION"]
        azure_endpoint = st.secrets["AZUREOPENAI_ENDPOINT"]
        azure_deployment_name = st.secrets["DEPLOYMENT_NAME"]


    else:
        raise ImportError("Streamlit secrets not found")

except Exception:
    # --- Local Development (.env) fallback ---
    from dotenv import load_dotenv
    load_dotenv()

    azure_openai_api_key = os.getenv("AZUREOPENAI_API_KEY")
    azure_api_version = os.getenv("AZUREOPENAI_API_VERSION")
    azure_endpoint = os.getenv("AZUREOPENAI_ENDPOINT")
    azure_deployment_name = os.getenv("DEPLOYMENT_NAME")

    