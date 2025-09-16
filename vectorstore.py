# vectorstore.py
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Persist directory for Chroma
CHROMA_DIR = os.path.join(os.getcwd(), "chroma_db")


class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embeddings
        )

    def add_mood_doc(self, mood_text: str, story_theme: str, activity_theme: str, date_time: str, uid: str):
        """Add one mood journal entry as a document into Chroma."""
        content = f"Mood: {mood_text}\nStory theme: {story_theme}\nActivity theme: {activity_theme}\nDate: {date_time}"
        metadata = {
            "mood_text": mood_text,
            "story_theme": story_theme,
            "activity_theme": activity_theme,
            "date_time": date_time,
            "uid": uid
        }
        doc = Document(page_content=content, metadata=metadata)
        self.vectordb.add_documents([doc], ids=[uid])

    def query_similar(self, query: str, k: int = 3):
        """Return similar past moods using Maximal Marginal Relevance (MMR)."""
        retriever = self.vectordb.as_retriever(
            search_type="mmr", search_kwargs={"k": k, "fetch_k": 10}
        )
        return retriever.invoke(query)
