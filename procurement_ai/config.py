try:
    import streamlit as st

    # Check that Streamlit secrets exist (running in Streamlit environment)
    if hasattr(st, "secrets") and "AZUREOPENAI_API_KEY" in st.secrets:

        # Azure OpenAI LLM configuration
        azure_api_key = st.secrets["AZUREOPENAI_API_KEY"]
        azure_api_version = st.secrets["AZUREOPENAI_API_VERSION"]
        azure_endpoint = st.secrets["AZUREOPENAI_ENDPOINT"]
        azure_deployment = st.secrets["DEPLOYMENT_NAME"]

        # Azure OpenAI Embedding Model configuration
        azure_api_key_embed = st.secrets["AZURE_OPENAI_API_KEY_EMBED"]
        azure_endpoint_embed = st.secrets["AZURE_OPENAI_ENDPOINT_EMBED"]
        azure_api_version_embed = st.secrets["AZURE_OPENAI_API_VERSION_EMBED"]

        # OpenAI (Transcription service) configuration
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        openai_deployment_name = st.secrets["OPENAI_DEPLOYMENT_NAME"]
        openai_api_version = st.secrets["OPENAI_API_VERSION"]
        openai_endpoint = st.secrets["OPENAI_ENDPOINT"]

    else:
        raise KeyError("Streamlit secrets not found or missing required keys")

except Exception:
    # Fallback to environment variables using .env file
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Azure OpenAI LLM configuration
    azure_api_key = os.getenv("AZUREOPENAI_API_KEY")
    azure_api_version = os.getenv("AZUREOPENAI_API_VERSION")
    azure_endpoint = os.getenv("AZUREOPENAI_ENDPOINT")
    azure_deployment = os.getenv("DEPLOYMENT_NAME")

    # Azure OpenAI Embedding Model configuration
    azure_api_key_embed = os.getenv("AZURE_OPENAI_API_KEY_EMBED")
    azure_endpoint_embed = os.getenv("AZURE_OPENAI_ENDPOINT_EMBED")
    azure_api_version_embed = os.getenv("AZURE_OPENAI_API_VERSION_EMBED")

    # OpenAI (Transcription service) configuration
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    openai_api_version = os.getenv("OPENAI_API_VERSION")
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
