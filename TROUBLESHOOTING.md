# Troubleshooting Log — RAG Pipeline Development

A professional documentation of all issues encountered and resolved during the development of the RAG pipeline project.

---

## Table of Contents

1. [Jupyter Kernel Not Using Virtual Environment](#1-jupyter-kernel-not-using-virtual-environment)
2. [LangChain Module Import Errors](#2-langchain-module-import-errors)
3. [Typo in LangChain Document Constructor](#3-typo-in-langchain-document-constructor)
4. [Duplicate Virtual Environments](#4-duplicate-virtual-environments)
5. [Groq Model Decommissioned Error](#5-groq-model-decommissioned-error)
6. [ModuleNotFoundError — sentence-transformers](#6-modulenotfounderror--sentence-transformers)
7. [ModuleNotFoundError — scikit-learn](#7-modulenotfounderror--scikit-learn)
8. [Python Module Resolution Error — src Package](#8-python-module-resolution-error--src-package)
9. [Empty search.py — Missing RAGSearch Class](#9-empty-searchpy--missing-ragsearch-class)
10. [FAISS Index Not Found on First Run](#10-faiss-index-not-found-on-first-run)
11. [Incorrect Data Directory Path](#11-incorrect-data-directory-path)

---

## 1. Jupyter Kernel Not Using Virtual Environment

**Error:**
```
ModuleNotFoundError: No module named 'langchain_core'
```

**Root Cause:**
Jupyter was using the system Python interpreter instead of the project's `.venv` virtual environment. Packages installed via `uv` were installed into `.venv` but Jupyter could not find them.

**Resolution:**
```bash
uv add ipykernel
uv run python -m ipykernel install --user --name=ragyt
```
Then select the `ragyt` kernel in the VS Code notebook kernel picker (top-right corner).

**Verification:**
```python
import sys
print(sys.executable)
# Expected: D:\data_projects\ragyt\.venv\Scripts\python.exe
```

---

## 2. LangChain Module Import Errors

**Error:**
```
No module named 'langchain.text_splitter'
No module named 'langchain.prompts'
No module named 'langchain.schema'
```

**Root Cause:**
LangChain underwent a major restructuring in newer versions. Core classes were moved out of the main `langchain` package into dedicated sub-packages.

**Resolution:**

| ❌ Old Import | ✅ New Import |
|---|---|
| `langchain.text_splitter` | `langchain_text_splitters` |
| `langchain.prompts` | `langchain_core.prompts` |
| `langchain.schema` | `langchain_core.messages` |
| `langchain.embeddings` | `langchain_community.embeddings` |
| `langchain.vectorstores` | `langchain_community.vectorstores` |
| `langchain.document_loaders` | `langchain_community.document_loaders` |

Install the missing package:
```bash
uv add langchain-text-splitters
```

**General Rule:** If `langchain.something` fails — check `langchain_core` for base classes and `langchain_community` for third-party integrations.

---

## 3. Typo in LangChain Document Constructor

**Error:**
```
TypeError: Document.__init__() missing 1 required positional argument: 'page_content'
```

**Root Cause:**
The `page_content` argument was misspelled as `page_contents` (with an extra `s`).

**Resolution:**
```python
# ❌ Incorrect
doc = Document(page_contents="...", metadata={})

# ✅ Correct
doc = Document(page_content="...", metadata={})
```

---

## 4. Duplicate Virtual Environments

**Warning:**
```
warning: `VIRTUAL_ENV=.venv-1` does not match the project environment path `.venv` and will be ignored
```

**Root Cause:**
VS Code's Python extension automatically created a second virtual environment (`.venv-1`) because `.venv` was already present or being created simultaneously by `uv`.

**Resolution:**
```bash
# Deactivate current environment
deactivate

# Delete the duplicate environment
rd /s /q .venv-1

# Set correct interpreter in VS Code
# Ctrl + Shift + P → Python: Select Interpreter → .venv\Scripts\python.exe
```

**Prevention:**
Create `.vscode/settings.json` in the project root:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true
}
```

---

## 5. Groq Model Decommissioned Error

**Error:**
```
BadRequestError: Error code: 400 - The model `gemma2-9b-it` has been decommissioned
and is no longer supported.
```

**Root Cause:**
The Groq model `gemma2-9b-it` was deprecated and removed from Groq's available models.

**Resolution:**
Replace the model name with an actively supported model:
```python
# ❌ Decommissioned
llm = ChatGroq(model="gemma2-9b-it")

# ✅ Active models (as of 2025)
llm = ChatGroq(model="llama-3.1-8b-instant")   # fast, lightweight
llm = ChatGroq(model="llama-3.3-70b-versatile") # more powerful
```

**Reference:** Always check [console.groq.com/docs/models](https://console.groq.com/docs/models) for currently supported models.

---

## 6. ModuleNotFoundError — sentence-transformers

**Error:**
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Root Cause:**
The `sentence-transformers` package was not installed in the active virtual environment. Additionally, Jupyter was pointing to the wrong Python kernel (`.venv-1` instead of `.venv`).

**Resolution:**
```bash
uv add sentence-transformers chromadb
```
Then restart the Jupyter kernel and re-run all cells.

---

## 7. ModuleNotFoundError — scikit-learn

**Error:**
```
ModuleNotFoundError: No module named 'sklearn'
```

**Root Cause:**
`scikit-learn` was not listed in `requirements.txt` and had not been installed.

**Resolution:**
```bash
uv add scikit-learn
```

---

## 8. Python Module Resolution Error — src Package

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Root Cause:**
The script was being executed from inside the `src/` directory, so Python could not resolve `src` as a package relative to the current working directory.

**Resolution — Option 1:** Add `sys.path` fix at the top of `app.py`:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**Resolution — Option 2:** Always run from the project root:
```bash
# ❌ Wrong
cd src
python app.py

# ✅ Correct
cd D:\data_projects\ragyt
uv run src/app.py
```

**Resolution — Option 3:** Create `__init__.py` inside `src/` to register it as a Python package:
```bash
echo. > src/__init__.py
```

---

## 9. Empty search.py — Missing RAGSearch Class

**Error:**
```
ImportError: cannot import name 'RAGSearch' from 'src.search'
```

**Root Cause:**
The `search.py` file was created but left completely empty. The `RAGSearch` class that `app.py` was trying to import did not exist.

**Resolution:**
Implemented the full `RAGSearch` class in `search.py` with the following responsibilities:
- Load the FAISS vector store
- Initialize the Groq LLM client
- Retrieve top-k relevant chunks for a query
- Build a context-aware prompt
- Return an LLM-generated answer

---

## 10. FAISS Index Not Found on First Run

**Error:**
```
RuntimeError: could not open faiss_store\faiss.index for reading: No such file or directory
```

**Root Cause:**
`store.load()` was called before `store.build_from_documents()`. The FAISS index file does not exist until it is explicitly built and saved on the first run.

**Resolution:**
On the **first run**, uncomment the build step in `app.py`:
```python
store.build_from_documents(docs)  # ✅ uncomment for first run
store.load()
```

On **subsequent runs**, comment it out to skip rebuilding:
```python
# store.build_from_documents(docs)  # comment out after first run
store.load()
```

---

## 11. Incorrect Data Directory Path

**Error:**
```
[DEBUG] Data path: D:\data_projects\ragyt\src\data
[DEBUG] Found 0 PDF files
```

**Root Cause:**
`app.py` was being run from inside the `src/` directory. The relative path `"data"` resolved to `src/data` instead of the project root `data/` folder.

**Resolution:**
Use an absolute path derived from the script's own location:
```python
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "data")
faiss_dir = os.path.join(project_root, "faiss_store")
```

This ensures paths always resolve correctly regardless of where the script is run from.

---

## Summary

| # | Issue | Category | Resolution |
|---|---|---|---|
| 1 | Jupyter using wrong Python | Environment | Register `.venv` as ipykernel |
| 2 | LangChain import errors | Dependency | Use new `langchain_core` / `langchain_community` imports |
| 3 | `page_contents` typo | Code | Rename to `page_content` |
| 4 | Duplicate `.venv-1` | Environment | Delete `.venv-1`, fix VS Code interpreter |
| 5 | Groq model deprecated | API | Switch to `llama-3.1-8b-instant` |
| 6 | `sentence-transformers` missing | Dependency | `uv add sentence-transformers` |
| 7 | `scikit-learn` missing | Dependency | `uv add scikit-learn` |
| 8 | `src` not recognized as package | Project Structure | Add `sys.path` fix + `__init__.py` |
| 9 | `search.py` was empty | Code | Implement `RAGSearch` class |
| 10 | FAISS index missing on first run | Logic | Call `build_from_documents()` before `load()` |
| 11 | Wrong data directory path | Project Structure | Use absolute path from `__file__` |
