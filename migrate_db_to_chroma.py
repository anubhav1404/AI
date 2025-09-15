# migrate_db_to_chroma.py
from database import fetch_entries   # reuse your ORM
from vectorstore import init_vectorstore, add_mood_doc

def migrate_to_chroma(limit=100):
    vectordb = init_vectorstore()

    entries = fetch_entries(limit=limit)
    print(f"Found {len(entries)} rows in Postgres.")

    for e in entries:
        uid = f"mood_{e.mood_id}"
        add_mood_doc(
            vectordb,
            mood_text=e.mood_text,
            story_theme=e.story_theme,
            activity_theme=e.activity_theme,
            date_time=e.date_time.strftime("%Y-%m-%d %H:%M"),
            uid=uid
        )
        print(f"✅ Migrated: {uid}")

    print("🎉 Migration complete!")

if __name__ == "__main__":
    migrate_to_chroma()
