# crud.py
from database import SessionLocal, MoodJournal

# Insert a new entry
def insert_entry(mood_text, story, activity):
    db = SessionLocal()
    entry = MoodJournal(mood_text=mood_text, story=story, activity=activity)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    db.close()
    return entry

# Fetch last N entries
def fetch_entries(limit=5):
    db = SessionLocal()
    entries = db.query(MoodJournal).order_by(MoodJournal.created_at.desc()).limit(limit).all()
    db.close()
    return entries

