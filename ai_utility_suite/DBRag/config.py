# Import necessary libraries
import os
import psycopg2

# Try to load from Streamlit secrets first
try:
    import streamlit as st

    if hasattr(st, "secrets") and "AZURE_OPENAI_API_KEY" in st.secrets:
        # -----------------------------
        # Azure OpenAI (LLM)
        # -----------------------------
        azure_openai_api_key = st.secrets["AZURE_OPENAI_API_KEY"]
        azure_api_version = st.secrets["AZURE_API_VERSION"]
        azure_endpoint = st.secrets["AZURE_ENDPOINT"]

        # -----------------------------
        # OpenAI (Transcription)
        # -----------------------------
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        openai_deployment_name = st.secrets["OPENAI_DEPLOYMENT_NAME"]
        openai_api_version = st.secrets["OPENAI_API_VERSION"]
        openai_endpoint = st.secrets["OPENAI_ENDPOINT"]

        # -----------------------------
        # Database (PostgreSQL)
        # -----------------------------
        db_name = st.secrets["DB_NAME"]
        db_user = st.secrets["DB_USER"]
        db_password = st.secrets["DB_PASSWORD"]
        db_host = st.secrets["DB_HOST"]
        db_port = st.secrets["DB_PORT"]
        ssl_mode = st.secrets.get("SSL_MODE", "disable")

    else:
        raise ImportError("Streamlit secrets not found")

except Exception:
    # -----------------------------
    # Local development mode (.env)
    # -----------------------------
    from dotenv import load_dotenv
    load_dotenv()

    # -----------------------------
    # Azure OpenAI (LLM)
    # -----------------------------
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_api_version = os.getenv("AZURE_API_VERSION")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")

    # -----------------------------
    # OpenAI (Transcription)
    # -----------------------------
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    openai_api_version = os.getenv("OPENAI_API_VERSION")
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")

    # -----------------------------
    # Database (PostgreSQL)
    # -----------------------------
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    ssl_mode = os.getenv("SSL_MODE", "disable")

# -----------------------------
# PostgreSQL Connection Setup
# -----------------------------
try:
    conn = psycopg2.connect(
        dbname=db_name,         # Name of the database
        user=db_user,           # Database username
        password=db_password,   # User password
        host=db_host,           # Database host/IP
        port=db_port,           # Database port
        sslmode=ssl_mode        # SSL mode, defaulting to 'disable' if not set
    )

    # Build the connection string
    connection_string = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"
    )

    # Create a cursor object to execute SQL queries and fetch results
    cursor = conn.cursor()

except Exception as e:
    conn = None
    cursor = None
    connection_string = None
    print(f"⚠️ Database connection not established: {e}")
