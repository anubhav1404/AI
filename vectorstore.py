# vectorstore.py
import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# persist directory for chroma. Adjust if you want another location.
CHROMA_DIR = os.path.join(os.getcwd(), "chroma_db")

def get_embeddings():
    """
    Use a small, fast sentence-transformers model for prototyping.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def init_vectorstore():
    """
    Initialize or load a Chroma vectorstore.
    Returns a Chroma instance (embedding_function already set).
    """
    embeddings = get_embeddings()
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return vectordb

def add_mood_doc(vectordb: Chroma, mood_text: str, story_theme: str, activity_theme: str, date_time: str, uid: str):
    """
    Add one mood journal entry as a document into Chroma.
    uid should be unique for each row (e.g., mood_{mood_id}).
    """
    content = f"Mood: {mood_text}\nStory theme: {story_theme}\nActivity theme: {activity_theme}\nDate: {date_time}"
    metadata = {
        "mood_text": mood_text,
        "story_theme": story_theme,
        "activity_theme": activity_theme,
        "date_time": date_time,
        "uid": uid
    }
    doc = Document(page_content=content, metadata=metadata)
    vectordb.add_documents([doc], ids=[uid])

def query_similar(vectordb: Chroma, query: str, k: int = 3):
    """
    Return a list of Document objects (page_content + metadata).
    Uses Maximal Marginal Relevance (MMR) to ensure diversity.
    """
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": 10})
    return retriever.invoke(query)

