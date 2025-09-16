# vectorstore.py
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os

CHROMA_DIR = os.path.join(os.getcwd(), "chroma_db")

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=self.embeddings)

    def add_mood_doc(self, mood_text, story_theme, activity_theme, date_time, uid):
        content = f"Mood: {mood_text}\nStory theme: {story_theme}\nActivity theme: {activity_theme}\nDate: {date_time}"
        metadata = {
            "mood_text": mood_text,
            "story_theme": story_theme,
            "activity_theme": activity_theme,
            "date_time": date_time,
            "uid": uid,
        }
        doc = Document(page_content=content, metadata=metadata)
        self.vectordb.add_documents([doc], ids=[uid])

    def query_similar(self, query: str, k: int = 3, strict: bool = False):
        retriever = self.vectordb.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": 10})
        docs = retriever.invoke(query)

        # Strict filtering: only return docs where mood_text matches exactly
        if strict:
            docs = [d for d in docs if d.metadata.get("mood_text", "").lower() == query.lower()]
        return docs
