# database.py
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from vectorstore import init_vectorstore, add_mood_doc

# ----------------- Database Setup -----------------
DB_URL = "sqlite:///moodai.db"
# allow cross-thread usage if Streamlit spawns threads
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class MoodJournal(Base):
    __tablename__ = "mood_journal"
    mood_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_time = Column(DateTime, default=datetime.utcnow)
    mood_text = Column(String, nullable=False)
    story_theme = Column(String, nullable=False)
    activity_theme = Column(String, nullable=False)
    music_summary = Column(String, nullable=True)

Base.metadata.create_all(engine)

# initialize vectordb (only once, import-safe)
try:
    VECTORDB = init_vectorstore()
except Exception as e:
    print("Warning: Could not initialize vectorstore:", e)
    VECTORDB = None

def insert_entry(mood_text, story_theme, activity_theme, music_summary=None):
    """
    Insert into sqlite and also add to Chroma vectordb (if available).
    """
    session = SessionLocal()
    try:
        entry = MoodJournal(
            mood_text=mood_text,
            story_theme=story_theme,
            activity_theme=activity_theme,
            music_summary=music_summary
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)

        uid = f"mood_{entry.mood_id}"
        date_str = entry.date_time.strftime("%Y-%m-%d %H:%M:%S")

        # add to Chroma vectorstore (best-effort)
        if VECTORDB:
            try:
                add_mood_doc(VECTORDB, mood_text, story_theme, activity_theme, date_str, uid)
            except Exception as e:
                print("Warning: failed to add to vectorstore:", e)
    finally:
        session.close()

def fetch_entries(limit=10):
    session = SessionLocal()
    try:
        rows = (
            session.query(MoodJournal)
            .order_by(MoodJournal.date_time.desc())
            .limit(limit)
            .all()
        )
        return rows
    finally:
        session.close()
