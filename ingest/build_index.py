
import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_documents(notes_dir):
    docs = []
    for subject in os.listdir(notes_dir):
        subject_path = os.path.join(notes_dir, subject)
        if not os.path.isdir(subject_path):
            continue
        for fname in os.listdir(subject_path):
            fpath = os.path.join(subject_path, fname)
            try:
                if fname.endswith('.pdf'):
                    loader = PyPDFLoader(fpath)
                elif fname.endswith(('.txt', '.md')):
                    loader = TextLoader(fpath)
                else:
                    continue
                loaded = loader.load()
                for d in loaded:
                    d.metadata['subject'] = subject
                    d.metadata['source_file'] = fname
                docs.extend(loaded)
            except Exception as e:
                print(f"Failed to load {fpath}: {e}")
    return docs

def build_index(notes_dir, persist_dir, local_dir="/content/chroma_db_local"):
    documents = load_documents(notes_dir)
    print(f"Loaded {len(documents)} document(s)")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    shutil.rmtree(local_dir, ignore_errors=True)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=local_dir
    )
    print(f"Stored {vectorstore._collection.count()} chunks locally")

    shutil.rmtree(persist_dir, ignore_errors=True)
    shutil.copytree(local_dir, persist_dir)
    print(f"Copied to {persist_dir}")

    return vectorstore

if __name__ == "__main__":
    base = "/content/drive/MyDrive/cortex"
    build_index(f"{base}/notes", f"{base}/chroma_db")
