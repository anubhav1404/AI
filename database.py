# database.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Read DB_URL from env; fallback to SQLite for local dev
DB_URL = os.getenv("DATABASE_URL", "sqlite:///moodai.db")
# If using Postgres in Docker, DATABASE_URL will be like:
# postgresql+psycopg2://user:pass@db:5432/moodai_db

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
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

# Create tables if not exist
Base.metadata.create_all(engine)

def insert_entry(mood_text, story_theme, activity_theme, music_summary=None):
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
        return entry
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
