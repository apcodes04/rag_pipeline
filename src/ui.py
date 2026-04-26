import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Pipeline",
    page_icon="🧠",
    layout="centered"
)

# ─── Title ─────────────────────────────────────────────────────
st.title("🧠 RAG Pipeline")
st.markdown("Ask anything from your documents!")
st.divider()

# ─── Initialize RAG (only once) ────────────────────────────────
@st.cache_resource
def load_rag():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faiss_dir = os.path.join(project_root, "faiss_store")
    return RAGSearch(persist_dir=faiss_dir)

try:
    rag = load_rag()
    st.success("✅ Documents loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load RAG: {e}")
    st.info("💡 Make sure you have built the FAISS index first by running app.py once!")
    st.stop()

# ─── Chat History ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─── Chat Input ────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about your documents..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                answer = rag.search_and_summarize(prompt, top_k=3)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    top_k = st.slider("Number of chunks to retrieve", min_value=1, max_value=10, value=3)
    st.caption("Higher = more context but slower")

    st.divider()

    st.header("📁 Supported Formats")
    st.markdown("""
    - 📄 PDF
    - 📝 TXT
    - 📊 CSV
    - 📋 Excel
    - 📃 Word
    - 🗂️ JSON
    """)

    st.divider()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Built by ADITYA PAWAR with LangChain, FAISS & Groq 🚀")