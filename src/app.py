import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    faiss_dir = os.path.join(project_root, "faiss_store")

    # Load documents
    docs = load_all_documents(data_dir)
    print(f"✅ Loaded {len(docs)} documents.")

    # Build vector store
    store = FaissVectorStore(faiss_dir)
    store.build_from_documents(docs)
    print("✅ FAISS index built successfully!")
    print("🚀 Now run: uv run streamlit run src/ui.py")