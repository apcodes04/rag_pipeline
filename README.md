# RAG Pipeline — Retrieval-Augmented Generation System

A modular, end-to-end RAG pipeline built with Python, LangChain, FAISS, and Groq LLaMA 3.1. This system ingests multi-format documents, generates semantic embeddings, stores them in a FAISS vector index, and answers natural language queries using an LLM.

---

## 🏗️ Project Structure

```
ragyt/
│
├── src/
│   ├── __init__.py
│   ├── app.py              ← Entry point
│   ├── data_loader.py      ← Loads documents from data/
│   ├── embedding.py        ← Chunks and embeds documents
│   ├── vectorstore.py      ← FAISS vector store management
│   └── search.py           ← RAG search and LLM answer generation
│
├── data/                   ← Drop your documents here
│   └── pdf/
│
├── notebook/               ← Jupyter notebooks for experimentation
│
├── faiss_store/            ← Auto-generated FAISS index (after first run)
│
├── .env                    ← Your API keys (never commit this!)
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

---

## 🧠 Architecture

```
Documents (PDF, TXT, CSV, DOCX, XLSX, JSON)
        ↓
  data_loader.py       → Loads all supported file formats
        ↓
  embedding.py         → Chunks text + generates embeddings via Sentence Transformers
        ↓
  vectorstore.py       → Stores & retrieves vectors using FAISS
        ↓
  search.py            → Retrieves top-k chunks + sends to Groq LLM
        ↓
  Natural Language Answer
```

---

## 🛠️ Technologies Used

**Languages & Frameworks:** Python, LangChain, LangChain-Community, LangChain-Core

**Tools & Libraries:** FAISS, Sentence Transformers, Groq (LLaMA 3.1), HuggingFace, NumPy, Scikit-learn, PyPDF, PyMuPDF, ChromaDB, python-dotenv, uv

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- A [Groq API key](https://console.groq.com/)

---

### Step 1 — Clone the repository
```bash
git clone https://github.com/your-username/ragyt.git
cd ragyt
```

### Step 2 — Install dependencies
```bash
uv add -r requirements.txt
```

### Step 3 — Set up your environment variables

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 4 — Add your documents

Drop any supported files into the `data/` folder:
```
data/
├── your_document.pdf
├── your_notes.txt
└── your_data.csv
```

Supported formats: **PDF, TXT, CSV, DOCX, XLSX, JSON**

---

## 🚀 How to Run

> ⚠️ Always run from the **project root**, not from inside `src/`

### First Run — Build the FAISS index
Make sure `store.build_from_documents(docs)` is **uncommented** in `app.py`, then run:
```bash
uv run src/app.py
```

This will:
1. Load all documents from `data/`
2. Chunk and embed them
3. Save the FAISS index to `faiss_store/`
4. Answer your query

### Subsequent Runs — Use saved index
After the first run, comment out `store.build_from_documents(docs)` in `app.py` to skip rebuilding:
```python
# store.build_from_documents(docs)  # comment this out after first run
```

Then run normally:
```bash
uv run src/app.py
```

### Change the query
Edit this line in `app.py`:
```python
query = "Your question here?"
```

---

## 📓 Jupyter Notebooks

To experiment interactively:
```bash
uv add jupyter ipykernel
uv run python -m ipykernel install --user --name=ragyt
uv run jupyter notebook
```

Then open any notebook in the `notebook/` folder and select the **ragyt** kernel.

---

## 📦 Requirements

```
langchain
langchain-core
langchain-community
langchain-groq
langchain-text-splitters
sentence-transformers
faiss-cpu
chromadb
pypdf
pymupdf
numpy
scikit-learn
python-dotenv
ipykernel
jupyter
Streamlit
```

'uv add -r requirements.txt' to add all the dependencies required for thr project.
---

## 🔐 Security

- Never commit your `.env` file
- Add `.env` to `.gitignore` before pushing to GitHub
- Rotate your Groq API key if accidentally exposed

---

# Step 1 — Build index (first time or when adding new documents)
uv run src/app.py

# Step 2 — Launch Streamlit UI
uv run streamlit run src/ui.py

## 📄 License

MIT License — feel free to use and modify for your own projects.

---

## 🙋 Author

Built by **Aditya Pawar** as a learning project to understand Retrieval-Augmented Generation systems from scratch.