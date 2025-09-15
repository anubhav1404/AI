# migrate_db_to_chroma.py
from database import fetch_entries, SessionLocal
from vectorstore import init_vectorstore, add_mood_doc
from sqlalchemy import select
from database import MoodJournal, engine

def backfill_all():
    vectordb = init_vectorstore()
    session = SessionLocal()
    try:
        rows = session.query(MoodJournal).order_by(MoodJournal.mood_id.asc()).all()
        for r in rows:
            uid = f"mood_{r.mood_id}"
            date_str = r.date_time.strftime("%Y-%m-%d %H:%M:%S")
            # avoid duplicates: Chroma will overwrite if same id exists
            add_mood_doc(vectordb, r.mood_text, r.story_theme, r.activity_theme, date_str, uid)
        print("Backfill completed.")
    finally:
        session.close()

if __name__ == "__main__":
    backfill_all()
