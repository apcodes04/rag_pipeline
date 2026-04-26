import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "faiss_store",
        model: str = "llama-3.1-8b-instant"
    ):
        self.store = FaissVectorStore(persist_dir)
        self.store.load()
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=model
        )
        print(f"[INFO] RAGSearch initialized with model: {model}")

    def search_and_summarize(self, query: str, top_k: int = 3) -> str:
        # Step 1 — retrieve relevant chunks
        print(f"[INFO] Searching for: '{query}'")
        results = self.store.query(query, top_k=top_k)

        if not results:
            return "No relevant documents found."

        # Step 2 — build context from retrieved chunks
        context = "\n\n".join([
            r["metadata"]["text"]
            for r in results
            if r["metadata"] and "text" in r["metadata"]
        ])

        if not context.strip():
            return "Retrieved documents had no readable content."

        # Step 3 — build prompt and call LLM
        prompt = f"""You are a helpful assistant. Use the context below to answer the question.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: {query}

Answer:"""

        print(f"[INFO] Sending prompt to LLM...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


if __name__ == "__main__":
    rag = RAGSearch()
    query = "Kepler's 1st law?"
    answer = rag.search_and_summarize(query, top_k=3)
    print("Answer:", answer)