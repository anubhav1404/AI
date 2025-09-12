from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------- Database Setup -----------------
DB_URL = "sqlite:///moodai.db"
engine = create_engine(DB_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class MoodJournal(Base):
    __tablename__ = "mood_journal"
    
    mood_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date_time = Column(DateTime, default=datetime.utcnow)
    mood_text = Column(String, nullable=False)
    story_theme = Column(String, nullable=False)
    activity_theme = Column(String, nullable=False)

Base.metadata.create_all(engine)

def insert_entry(mood_text, story_theme, activity_theme):
    session = SessionLocal()
    entry = MoodJournal(
        mood_text=mood_text,
        story_theme=story_theme,
        activity_theme=activity_theme
    )
    session.add(entry)
    session.commit()
    session.close()

def fetch_entries(limit=10):
    session = SessionLocal()
    rows = (
        session.query(MoodJournal)
        .order_by(MoodJournal.date_time.desc())
        .limit(limit)
        .all()
    )
    session.close()
    return rows

