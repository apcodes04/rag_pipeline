import os
import streamlit as st

def get_secret(key: str, default: str = "") -> str:
    """Get secret from HF Space secrets, env vars, or fallback"""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, default)

# ─── Environment Detection ─────────────────────────────────────
IS_LOCAL = os.getenv("ENVIRONMENT", "local") == "local"

# ─── Redirect URI ──────────────────────────────────────────────
if IS_LOCAL:
    REDIRECT_URI = "http://localhost:8501/component/streamlit_oauth.authorize_button/index.html"
else:
    REDIRECT_URI = "https://apcodes-rag-pipeline.hf.space/component/streamlit_oauth.authorize_button/index.html"

# ─── Auth ──────────────────────────────────────────────────────
GOOGLE_CLIENT_ID     = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")

# ─── Database ──────────────────────────────────────────────────
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# ─── LLM ───────────────────────────────────────────────────────
GROQ_API_KEY = get_secret("GROQ_API_KEY")

# ─── Admin ─────────────────────────────────────────────────────
ADMIN_EMAIL = "apcodes04@gmail.com"