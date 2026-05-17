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

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Pipeline — Chat with Your Docs",
    page_icon="🧠",
    layout="centered"
)

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
    .fact-emoji {
        font-size: 1.4rem;
        margin-right: 8px;
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
    .progress-step.done {
        border-left: 3px solid #10B981;
        color: #e2e8f0;
    }
    .progress-step.active {
        border-left: 3px solid #6366F1;
        color: #e2e8f0;
    }
    .stat-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        margin: 4px;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 900;
        color: #10B981;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Dynamic Facts ─────────────────────────────────────────────
AI_FACTS = [
    ("🧠", "RAG stands for Retrieval-Augmented Generation — it finds relevant info BEFORE asking the AI, so answers are grounded in your actual documents!"),
    ("⚡", "FAISS (Facebook AI Similarity Search) can search through 1 million vectors in under 10 milliseconds — faster than you can blink!"),
    ("🔢", "Your documents are being converted into arrays of 384 numbers called embeddings — each number captures a tiny piece of meaning!"),
    ("🌍", "The model being used — LLaMA 3.1 — was trained on over 15 trillion tokens of text from across the internet!"),
    ("🎯", "Sentence Transformers turn similar sentences into similar numbers — so 'dog' and 'puppy' end up much closer than 'dog' and 'spaceship'!"),
    ("📚", "Without RAG, AI models can hallucinate — make up facts that sound real but aren't. RAG fixes this by forcing the AI to read YOUR documents first!"),
    ("🔍", "Vector search understands MEANING not just keywords — so even if you ask differently than the document is written, it still finds the right answer!"),
    ("💡", "The chunk size in this pipeline is 1000 characters with 200 character overlap — the overlap ensures no important context gets cut off at boundaries!"),
    ("🚀", "Groq's inference speed is up to 10x faster than traditional GPU inference — that's why answers come back so quickly!"),
    ("📊", "The more chunks retrieved (top_k), the more context the LLM has — this pipeline retrieves top 20 chunks for maximum accuracy!"),
    ("🧩", "LangChain acts like LEGO bricks for AI — each piece (loader, splitter, embedder, retriever) snaps together to build the full pipeline!"),
    ("🔐", "Your documents never leave your machine during processing — embeddings are generated locally using Sentence Transformers!"),
    ("📐", "Cosine similarity measures the angle between two vectors — a score of 1.0 means identical meaning, 0.0 means completely unrelated!"),
    ("🎲", "Each chunk of your document gets its own unique fingerprint (embedding) — no two chunks have exactly the same fingerprint!"),
    ("🌐", "ChromaDB, FAISS, and Pinecone are all vector databases — this pipeline uses FAISS because it's lightning fast and runs completely offline!"),
]

def get_random_fact():
    return random.choice(AI_FACTS)

# ─── Project paths ─────────────────────────────────────────────
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
faiss_dir = os.path.join(project_root, "faiss_store")
faiss_index_path = os.path.join(faiss_dir, "faiss.index")

# ─── Header ────────────────────────────────────────────────────
st.markdown('<p class="main-title">🧠 RAG Pipeline</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your documents — PDF, CSV, Word, JSON and more — then ask anything!</p>', unsafe_allow_html=True)
st.divider()

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
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
    - 📄 **PDF** — Books, papers, reports
    - 📝 **TXT** — Notes, logs, articles
    - 📊 **CSV** — Spreadsheet data
    - 📋 **XLSX** — Excel workbooks
    - 📃 **DOCX** — Word documents
    - 🗂️ **JSON** — Structured data
    """)

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Built by ADITYA PAWAR 🚀 contact the developer here: adityabpawar.work@gmail.com or LinkedIn : www.linkedin.com/in/aditya-pawar-345908401")

# ─── Building State — Show Progress + Facts ────────────────────
if st.session_state.get("building", False):
    uploaded_files = st.session_state.get("uploaded_files", [])

    st.markdown("## ⚙️ Building Your Knowledge Base")
    st.markdown("This may take a moment — sit back and learn something cool! 👇")
    st.markdown("")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Steps display
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

    # Rotating facts section
    fact_title = st.empty()
    fact_box = st.empty()

    fact_title.markdown("### 💡 Did you know?")

    def show_fact():
        emoji, fact = get_random_fact()
        fact_box.markdown(
            f'<div class="fact-box"><span class="fact-emoji">{emoji}</span>{fact}</div>',
            unsafe_allow_html=True
        )

    show_fact()

    try:
        # ── Step 1: Save files ──────────────────────────────────
        temp_dir = tempfile.mkdtemp()
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        progress_bar.progress(20)
        steps["save"].markdown(f'<div class="progress-step done">✅ Step 1 — Saved {len(uploaded_files)} file(s) successfully</div>', unsafe_allow_html=True)
        steps["load"].markdown('<div class="progress-step active">⏳ Step 2 — Loading document pages...</div>', unsafe_allow_html=True)
        show_fact()
        time.sleep(0.5)

        # ── Step 2: Load documents ──────────────────────────────
        docs = load_all_documents(temp_dir)
        progress_bar.progress(40)
        steps["load"].markdown(f'<div class="progress-step done">✅ Step 2 — Loaded {len(docs)} document page(s)</div>', unsafe_allow_html=True)
        steps["embed"].markdown('<div class="progress-step active">⏳ Step 3 — Generating embeddings (this takes the longest!)...</div>', unsafe_allow_html=True)
        show_fact()

        # Show stats so far
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(uploaded_files)}</div><div class="stat-label">Files uploaded</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(docs)}</div><div class="stat-label">Pages loaded</div></div>', unsafe_allow_html=True)
        with col3:
            est_chunks = len(docs) * 3
            st.markdown(f'<div class="stat-card"><div class="stat-number">~{est_chunks}</div><div class="stat-label">Est. chunks</div></div>', unsafe_allow_html=True)

        # ── Step 3 + 4: Build FAISS (embedding happens here) ───
        store = FaissVectorStore(faiss_dir)

        # Patch build to update progress mid-way
        show_fact()
        progress_bar.progress(60)

        store.build_from_documents(docs)

        progress_bar.progress(80)
        steps["embed"].markdown('<div class="progress-step done">✅ Step 3 — Embeddings generated successfully</div>', unsafe_allow_html=True)
        steps["store"].markdown('<div class="progress-step done">✅ Step 4 — Stored in FAISS vector database</div>', unsafe_allow_html=True)
        show_fact()

        # ── Step 5: Cleanup ─────────────────────────────────────
        shutil.rmtree(temp_dir)
        progress_bar.progress(100)
        steps["done"].markdown('<div class="progress-step done">✅ Step 5 — Knowledge base ready!</div>', unsafe_allow_html=True)
        status_text.success("🎉 Knowledge base built successfully! You can now ask questions.")

        # Reset building state
        st.session_state.building = False
        time.sleep(1.5)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error during processing: {e}")
        st.session_state.building = False
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    st.stop()

# ─── No knowledge base yet ─────────────────────────────────────
if not os.path.exists(faiss_index_path):
    st.markdown("### 👋 Welcome! Let's get started.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem">📤</div>
            <div class="stat-label" style="font-size:0.85rem; color:#e2e8f0; margin-top:8px">Step 1<br>Upload your files in the sidebar</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem">⚡</div>
            <div class="stat-label" style="font-size:0.85rem; color:#e2e8f0; margin-top:8px">Step 2<br>Click Build Knowledge Base</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem">💬</div>
            <div class="stat-label" style="font-size:0.85rem; color:#e2e8f0; margin-top:8px">Step 3<br>Ask anything from your docs!</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### 💡 While you wait — did you know?")
    emoji, fact = get_random_fact()
    st.markdown(
        f'<div class="fact-box"><span class="fact-emoji">{emoji}</span>{fact}</div>',
        unsafe_allow_html=True
    )
    st.stop()

# ─── Load RAG into session ─────────────────────────────────────
if "rag" not in st.session_state:
    with st.spinner("🔄 Loading knowledge base..."):
        try:
            st.session_state.rag = RAGSearch(persist_dir=faiss_dir)
        except Exception as e:
            st.error(f"❌ Failed to load knowledge base: {e}")
            st.stop()

# ─── Chat History ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─── Chat Input ────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about your documents..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching through your documents..."):
            try:
                answer = st.session_state.rag.search_and_summarize(prompt, top_k=20)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"❌ Error: {e}")

# uv run streamlit run src/ui.py