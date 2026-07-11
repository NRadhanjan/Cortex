
import os
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from mcp.server.fastmcp import FastMCP

# --- config ---
CHROMA_DIR = "/content/chroma_db_local"   # local copy, fast to load
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- setup (runs once when server starts) ---
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_model)
groq_client = Groq(api_key=GROQ_API_KEY)

mcp = FastMCP("Cortex Notes")

@mcp.tool()
def search_notes(query: str, k: int = 6) -> str:
    """Search the user's coursework notes (DSA, security, OS, DBMS, ML) and answer a question using retrieved context."""
    results = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([
        f"[Source: {r.metadata.get('source_file')}, Page: {r.metadata.get('page')}]\n{r.page_content}"
        for r in results
    ])

    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    mcp.run(transport="sse")
