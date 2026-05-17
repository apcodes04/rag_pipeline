import streamlit as st
import os
import json
import tempfile

def get_authenticator():
    try:
        from streamlit_google_auth import Authenticate

        # Build credentials from secrets/env
        credentials = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET", ""),
                "redirect_uris": [
                    os.getenv("REDIRECT_URI") or st.secrets.get("REDIRECT_URI", "http://localhost:8501")
                ],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        # Write credentials to a temp file
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        )
        json.dump(credentials, tmp)
        tmp.flush()

        authenticator = Authenticate(
            secret_credentials_path=tmp.name,
            redirect_uri=os.getenv("REDIRECT_URI") or st.secrets.get("REDIRECT_URI", "http://localhost:8501"),
            cookie_name="rag_pipeline_auth",
            cookie_key=os.getenv("COOKIE_SECRET") or st.secrets.get("COOKIE_SECRET", "ragyt-secret-2026"),
            cookie_expiry_days=30.0
        )
        return authenticator

    except Exception as e:
        st.error(f"❌ Auth setup failed: {e}")
        st.stop()

def show_login_page():
    st.markdown("""
    <style>
        .login-title {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #10B981, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        .login-subtitle {
            color: #888;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #6366F1;
        }
        .feature-title {
            font-weight: 700;
            color: #e2e8f0;
            font-size: 1rem;
        }
        .feature-desc {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="login-title">🧠 RAG Pipeline</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Chat with your documents — zero hallucinations!</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📄 Upload Any Document</div>
            <div class="feature-desc">PDF, CSV, Word, Excel, JSON, TXT</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">🔍 Semantic Search</div>
            <div class="feature-desc">Finds answers by meaning not just keywords</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">🤖 Zero Hallucinations</div>
            <div class="feature-desc">AI answers only from your documents</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 👇 Sign in with Google to get started")