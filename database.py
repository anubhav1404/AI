# database.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class MoodJournal(Base):
    __tablename__ = "mood_journal"
    mood_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_time = Column(DateTime, default=datetime.utcnow)
    mood_text = Column(String, nullable=False)
    story_theme = Column(String, nullable=False)
    activity_theme = Column(String, nullable=False)
    music_summary = Column(String, nullable=True)

class DatabaseManager:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL", "sqlite:///moodai.db")
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def insert_entry(self, mood_text, story_theme, activity_theme, music_summary=None):
        session = self.SessionLocal()
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

    def fetch_entries(self, limit=10):
        session = self.SessionLocal()
        try:
            return (
                session.query(MoodJournal)
                .order_by(MoodJournal.date_time.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()
