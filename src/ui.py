import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import tempfile
import shutil
import time
import random
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch
from src.data_loader import load_all_documents
from src.admin import show_admin_dashboard
from src.auth import get_oauth_client, show_login_page
from src.db import track_user_login, track_query, get_user_stats
import base64
import json
# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Pipeline — Chat with Your Docs",
    page_icon="🧠",
    layout="centered"
)

# ─── Auth ──────────────────────────────────────────────────────
REDIRECT_URI = os.getenv("REDIRECT_URI") or st.secrets.get("REDIRECT_URI", "http://localhost:8501")

if "user_email" not in st.session_state:
    show_login_page()
    oauth = get_oauth_client()

    result = oauth.authorize_button(
        name="Sign in with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google_login",
        extras_params={"prompt": "consent", "access_type": "offline"}
    )

    if result and "token" in result:
        id_token = result["token"].get("id_token", "")
        try:
            payload = id_token.split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            user_data = json.loads(base64.b64decode(payload).decode("utf-8"))
            st.session_state.user_email = user_data.get("email", "")
            st.session_state.user_name = user_data.get("name", "User")
            st.session_state.user_picture = user_data.get("picture", "")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to decode user info: {e}")
    st.stop()

# ─── User is logged in ─────────────────────────────────────────
user_email = st.session_state.get("user_email", "")
user_name = st.session_state.get("user_name", "User")
user_picture = st.session_state.get("user_picture", "")

# Track user login
track_user_login(user_email)
user_stats = get_user_stats(user_email)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #10B981, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .fact-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #6366F1;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 0.95rem;
        color: #e2e8f0;
        line-height: 1.6;
    }
    .progress-step {
        background: #1e293b;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 6px 0;
        font-size: 0.9rem;
        color: #94a3b8;
        border-left: 3px solid #334155;
    }
    .progress-step.done { border-left: 3px solid #10B981; color: #e2e8f0; }
    .progress-step.active { border-left: 3px solid #6366F1; color: #e2e8f0; }
    .stat-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        margin: 4px;
    }
    .stat-number { font-size: 1.8rem; font-weight: 900; color: #10B981; }
    .stat-label { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
    .user-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Dynamic Facts ─────────────────────────────────────────────
AI_FACTS = [
    ("🧠", "RAG stands for Retrieval-Augmented Generation — it finds relevant info BEFORE asking the AI!"),
    ("⚡", "FAISS can search through 1 million vectors in under 10 milliseconds — faster than a blink!"),
    ("🔢", "Your documents are converted into arrays of 384 numbers called embeddings!"),
    ("🌍", "LLaMA 3.1 was trained on over 15 trillion tokens of text from across the internet!"),
    ("🎯", "Sentence Transformers turn similar sentences into similar numbers automatically!"),
    ("📚", "Without RAG, AI models hallucinate — make up facts that sound real but aren't!"),
    ("🔍", "Vector search understands MEANING not just keywords!"),
    ("🚀", "Groq's inference speed is up to 10x faster than traditional GPU inference!"),
    ("📊", "This pipeline retrieves top 20 chunks for maximum accuracy!"),
    ("🧩", "LangChain acts like LEGO bricks for AI — each piece snaps together!"),
    ("🔐", "Your documents are processed locally — they never leave your machine!"),
    ("📐", "Cosine similarity of 1.0 means identical meaning, 0.0 means completely unrelated!"),
]

def get_random_fact():
    return random.choice(AI_FACTS)

# ─── Project paths ─────────────────────────────────────────────
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each user gets their own FAISS index!
faiss_dir = os.path.join(project_root, "faiss_store", user_email.replace("@", "_").replace(".", "_"))
faiss_index_path = os.path.join(faiss_dir, "faiss.index")

# ─── Header ────────────────────────────────────────────────────
st.markdown('<p class="main-title">🧠 RAG Pipeline</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your documents and ask anything — zero hallucinations!</p>', unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    # User profile
    if user_picture:
        st.image(user_picture, width=60)
    st.markdown(f"**{user_name}**")
    st.caption(f"📧 {user_email}")
    st.caption(f"💬 {user_stats.get('total_queries', 0)} queries made")

    st.divider()

    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        for key in ["user_email", "user_name", "user_picture", "rag", "messages"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.markdown("### 📁 Upload Documents")
    st.caption("Supported: PDF, TXT, CSV, DOCX, XLSX, JSON")

    uploaded_files = st.file_uploader(
        "Choose your files",
        type=["pdf", "txt", "csv", "docx", "xlsx", "json"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected!")
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")

    st.divider()

    if uploaded_files:
        if st.button("⚡ Build Knowledge Base", use_container_width=True, type="primary"):
            st.session_state.building = True
            st.session_state.uploaded_files = uploaded_files
            if "rag" in st.session_state:
                del st.session_state["rag"]
            st.rerun()

    st.divider()
    st.markdown("### 📋 Supported Formats")
    st.markdown("""
    - 📄 **PDF**
    - 📝 **TXT**
    - 📊 **CSV**
    - 📋 **XLSX**
    - 📃 **DOCX**
    - 🗂️ **JSON**
    """)

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Built by ADITYA PAWAR 🚀 contact the developer here: adityabpawar.work@gmail.com or LinkedIn : www.linkedin.com/in/aditya-pawar-345908401")

# ─── Building State ────────────────────────────────────────────
if st.session_state.get("building", False):
    uploaded_files = st.session_state.get("uploaded_files", [])

    st.markdown("## ⚙️ Building Your Knowledge Base")
    st.markdown("This may take a moment — sit back and learn something cool! 👇")

    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = {
        "save": st.empty(),
        "load": st.empty(),
        "embed": st.empty(),
        "store": st.empty(),
        "done": st.empty(),
    }

    steps["save"].markdown('<div class="progress-step active">⏳ Step 1 — Saving uploaded files...</div>', unsafe_allow_html=True)
    steps["load"].markdown('<div class="progress-step">⏸ Step 2 — Loading document pages</div>', unsafe_allow_html=True)
    steps["embed"].markdown('<div class="progress-step">⏸ Step 3 — Generating embeddings</div>', unsafe_allow_html=True)
    steps["store"].markdown('<div class="progress-step">⏸ Step 4 — Storing in FAISS vector DB</div>', unsafe_allow_html=True)
    steps["done"].markdown('<div class="progress-step">⏸ Step 5 — Finalizing knowledge base</div>', unsafe_allow_html=True)

    st.markdown("---")
    fact_title = st.empty()
    fact_box = st.empty()
    fact_title.markdown("### 💡 Did you know?")

    def show_fact():
        emoji, fact = get_random_fact()
        fact_box.markdown(
            f'<div class="fact-box"><span>{emoji}</span> {fact}</div>',
            unsafe_allow_html=True
        )

    show_fact()

    try:
        temp_dir = tempfile.mkdtemp()
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        progress_bar.progress(20)
        steps["save"].markdown(f'<div class="progress-step done">✅ Step 1 — Saved {len(uploaded_files)} file(s)</div>', unsafe_allow_html=True)
        steps["load"].markdown('<div class="progress-step active">⏳ Step 2 — Loading document pages...</div>', unsafe_allow_html=True)
        show_fact()
        time.sleep(0.5)

        docs = load_all_documents(temp_dir)
        progress_bar.progress(40)
        steps["load"].markdown(f'<div class="progress-step done">✅ Step 2 — Loaded {len(docs)} page(s)</div>', unsafe_allow_html=True)
        steps["embed"].markdown('<div class="progress-step active">⏳ Step 3 — Generating embeddings...</div>', unsafe_allow_html=True)
        show_fact()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(uploaded_files)}</div><div class="stat-label">Files uploaded</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(docs)}</div><div class="stat-label">Pages loaded</div></div>', unsafe_allow_html=True)
        with col3:
            est_chunks = len(docs) * 3
            st.markdown(f'<div class="stat-card"><div class="stat-number">~{est_chunks}</div><div class="stat-label">Est. chunks</div></div>', unsafe_allow_html=True)

        store = FaissVectorStore(faiss_dir)
        show_fact()
        progress_bar.progress(60)
        store.build_from_documents(docs)

        progress_bar.progress(80)
        steps["embed"].markdown('<div class="progress-step done">✅ Step 3 — Embeddings generated</div>', unsafe_allow_html=True)
        steps["store"].markdown('<div class="progress-step done">✅ Step 4 — Stored in FAISS vector DB</div>', unsafe_allow_html=True)
        show_fact()

        shutil.rmtree(temp_dir)
        progress_bar.progress(100)
        steps["done"].markdown('<div class="progress-step done">✅ Step 5 — Knowledge base ready!</div>', unsafe_allow_html=True)
        status_text.success("🎉 Knowledge base built! Start asking questions.")

        st.session_state.building = False
        time.sleep(1.5)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.building = False
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    st.stop()

# ─── No knowledge base ─────────────────────────────────────────
if not os.path.exists(faiss_index_path):
    st.markdown(f"### 👋 Welcome, {user_name}!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card"><div style="font-size:2rem">📤</div><div class="stat-label" style="font-size:0.85rem;color:#e2e8f0;margin-top:8px">Step 1<br>Upload files in sidebar</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div style="font-size:2rem">⚡</div><div class="stat-label" style="font-size:0.85rem;color:#e2e8f0;margin-top:8px">Step 2<br>Build Knowledge Base</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div style="font-size:2rem">💬</div><div class="stat-label" style="font-size:0.85rem;color:#e2e8f0;margin-top:8px">Step 3<br>Ask anything!</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### 💡 Did you know?")
    emoji, fact = get_random_fact()
    st.markdown(f'<div class="fact-box"><span>{emoji}</span> {fact}</div>', unsafe_allow_html=True)
    st.stop()

# ─── Load RAG ──────────────────────────────────────────────────
if "rag" not in st.session_state:
    with st.spinner("🔄 Loading your knowledge base..."):
        try:
            st.session_state.rag = RAGSearch(persist_dir=faiss_dir)
        except Exception as e:
            st.error(f"❌ Failed to load: {e}")
            st.stop()

# ─── Chat ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching your documents..."):
            try:
                answer = st.session_state.rag.search_and_summarize(prompt, top_k=20)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Track query
                track_query(
                    email=user_email,
                    query=prompt,
                    answer=answer,
                    tokens_used=len(prompt.split() + answer.split()) * 2
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")

                

# ─── Admin Dashboard (only visible to you) ─────────────────────
show_admin_dashboard(user_email)