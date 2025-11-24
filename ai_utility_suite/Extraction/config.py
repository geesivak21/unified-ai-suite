import os

try:
    import streamlit as st
    # Check if secrets are available (Streamlit Cloud)
    if hasattr(st, "secrets") and "DOCUMENTINTELLIGENCE_API_KEY" in st.secrets:
        # Azure Document Intelligence
        AZURE_KEY = st.secrets["DOCUMENTINTELLIGENCE_API_KEY"]
        AZURE_ENDPOINT = st.secrets["DOCUMENTINTELLIGENCE_ENDPOINT"]

        # Azure OpenAI
        OPENAI_API_KEY = st.secrets["AZUREOPENAI_API_KEY"]
        OPENAI_API_VERSION = st.secrets["AZUREOPENAI_API_VERSION"]
        OPENAI_ENDPOINT = st.secrets["AZUREOPENAI_ENDPOINT"]
        DEPLOYMENT = st.secrets["DEPLOYMENT_NAME"]

    else:
        raise ImportError("No Streamlit secrets found. Falling back to .env")

except Exception:
    # Local development mode — load from .env
    from dotenv import load_dotenv
    load_dotenv()

    # Azure Document Intelligence
    AZURE_KEY = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")
    AZURE_ENDPOINT = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")

    # Azure OpenAI
    OPENAI_API_KEY = os.getenv("AZUREOPENAI_API_KEY")
    OPENAI_API_VERSION = os.getenv("AZUREOPENAI_API_VERSION")
    OPENAI_ENDPOINT = os.getenv("AZUREOPENAI_ENDPOINT")
    DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")
