# migrate_db_to_chroma.py
import os
from database import DatabaseManager
from vectorstore import VectorStoreManager

# initialize managers
db = DatabaseManager()
vectormanager = VectorStoreManager()

# fetch all entries from Postgres
entries = db.fetch_entries(limit=1000)  # large limit to get all
print(f"Found {len(entries)} rows in Postgres.")

for e in entries:
    uid = f"mood_{e.mood_id}"
    vectormanager.add_mood_doc(
        mood_text=e.mood_text,
        story_theme=e.story_theme,
        activity_theme=e.activity_theme,
        date_time=str(e.date_time),
        uid=uid
    )
    print(f"✅ Migrated: {uid}")

print("🎉 Migration complete!")
