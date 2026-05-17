import streamlit as st
from streamlit_google_auth import Authenticate
import os

def get_authenticator():
    authenticator = Authenticate(
        secret_credentials_path=None,
        cookie_name="rag_pipeline_auth",
        cookie_key=os.getenv("COOKIE_SECRET", st.secrets.get("COOKIE_SECRET", "ragyt-secret-key-2026")),
        redirect_uri=os.getenv("REDIRECT_URI", st.secrets.get("REDIRECT_URI", "http://localhost:8501")),
        client_id=os.getenv("GOOGLE_CLIENT_ID", st.secrets.get("GOOGLE_CLIENT_ID", "")),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", st.secrets.get("GOOGLE_CLIENT_SECRET", ""))
    )
    return authenticator

def show_login_page():
    st.markdown("""
    <style>
        .login-container {
            text-align: center;
            padding: 60px 20px;
        }
        .login-title {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #10B981, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #888;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            text-align: left;
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
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">🧠 RAG Pipeline</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Chat with your documents using AI — zero hallucinations!</p>', unsafe_allow_html=True)

        # Features
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📄 Upload Any Document</div>
            <div class="feature-desc">PDF, CSV, Word, Excel, JSON, TXT — all supported</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">🔍 Semantic Search</div>
            <div class="feature-desc">Finds answers by meaning, not just keywords</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">🤖 Zero Hallucinations</div>
            <div class="feature-desc">AI answers only from your documents — never makes things up</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 👇 Sign in to get started")
        st.markdown('</div>', unsafe_allow_html=True)