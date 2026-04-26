import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

if __name__ == "__main__":
    # Get project root path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    faiss_dir = os.path.join(project_root, "faiss_store")

    # Load documents
    docs = load_all_documents(data_dir)
    print(f"Loaded {len(docs)} documents.")

    # Build vector store
    store = FaissVectorStore(faiss_dir)
    store.build_from_documents(docs)  # ✅ uncommented to build first time
    store.load()

    # Search
    rag_search = RAGSearch(persist_dir=faiss_dir)
    query = "Kepler's 1st law?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)