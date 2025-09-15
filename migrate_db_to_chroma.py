# migrate_sqlite_to_postgres.py
import os
import sqlite3
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

SQLITE_FILE = os.path.join(os.getcwd(), "moodai.db")
DATABASE_URL = os.getenv("DATABASE_URL")  # must be set to Postgres connection

if not DATABASE_URL:
    raise RuntimeError("Please set DATABASE_URL in environment (postgres connection string).")

# read from sqlite
if not os.path.exists(SQLITE_FILE):
    raise RuntimeError(f"SQLite file not found at {SQLITE_FILE}")

conn = sqlite3.connect(SQLITE_FILE)
cur = conn.cursor()

# fetch rows
cur.execute("""
    SELECT mood_id, date_time, mood_text, story_theme, activity_theme, music_summary
    FROM mood_journal
    ORDER BY mood_id ASC
""")
rows = cur.fetchall()
print(f"Found {len(rows)} rows in sqlite.")

# connect to postgres via SQLAlchemy engine
pg_engine = create_engine(DATABASE_URL)
with pg_engine.begin() as conn_pg:
    # ensure table exists (will create via SQLAlchemy if not)
    # The application (app container) should have created tables via Base.metadata.create_all,
    # but we can double-check/ensure here by creating the table using the same schema if needed.

    insert_sql = text("""
        INSERT INTO mood_journal (date_time, mood_text, story_theme, activity_theme, music_summary)
        VALUES (:date_time, :mood_text, :story_theme, :activity_theme, :music_summary)
    """)
    count = 0
    for r in rows:
        _, date_time, mood_text, story_theme, activity_theme, music_summary = r
        # date_time in sqlite may be string; Postgres will accept common formats
        conn_pg.execute(insert_sql, {
            "date_time": date_time,
            "mood_text": mood_text,
            "story_theme": story_theme,
            "activity_theme": activity_theme,
            "music_summary": music_summary
        })
        count += 1
    print(f"Inserted {count} rows into Postgres.")

conn.close()
