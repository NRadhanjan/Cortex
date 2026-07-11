
import os
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_vectorstore(persist_dir="/content/chroma_db_local"):
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_dir, embedding_function=embedding_model)

def answer_question(query, vectorstore, groq_client, k=6, model="llama-3.3-70b-versatile"):
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
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    vectorstore = load_vectorstore()
    print(answer_question("What is Big O notation?", vectorstore, groq_client))
