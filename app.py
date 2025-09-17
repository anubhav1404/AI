# app.py
import streamlit as st
from database import DatabaseManager
from chains import StoryActivityGenerator
from rag_chain import RAGGenerator
from music import MusicRecommender
from vectorstore import VectorStoreManager

# Initialize service classes
db = DatabaseManager()
generator = StoryActivityGenerator()
rag_generator = RAGGenerator()
music_rec = MusicRecommender()
vectormanager = VectorStoreManager()

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="MoodAI", layout="wide")
st.title("🎭 MoodAI - Your Personal Mood Storyteller")

# --- Inputs ---
mood = st.text_input("💭 How are you feeling today?", "")
language = st.selectbox("🎶 Preferred music language", ["Any", "English", "Hindi", "Punjabi", "Spanish", "K-Pop"])

col1, col2 = st.columns([3, 2])

# ----------------- Baseline Generation -----------------
if st.button("✨ Generate (baseline)"):
    if not mood:
        st.warning("Please enter your mood.")
    else:
        results = generator.generate(mood)
        # show story & activity
        with col1:
            st.subheader("📖 Story (baseline)")
            st.write(results.get("story", ""))
        with col2:
            st.subheader("🎯 Activity (baseline)")
            st.write(results.get("activity", ""))

        # music recommendations
        st.subheader("🎶 Music (baseline)")
        tracks, used_tag = music_rec.get_music_recommendation(mood, language=language, limit=4)
        if used_tag:
            st.caption(f"Last.fm tag used: {used_tag}")
        if tracks:
            cols = st.columns(len(tracks))
            for i, t in enumerate(tracks):
                with cols[i]:
                    if t.get("image"):
                        st.image(t["image"], width=150)
                    st.markdown(f"**[{t['title']}]({t['url']})**")
                    st.caption(f"by {t['artist']}")
                    st.write(f"👥 Listeners: {t['listeners']}")
        else:
            st.info("No music found for this mood.")

        # store to DB (short themes)
        story_theme = results.get("story", "").split(".")[0].strip() if results.get("story") else ""
        activity_theme = results.get("activity", "").split(",")[0].strip() if results.get("activity") else ""
        music_summary = f"{tracks[0]['title']} - {tracks[0]['artist']}" if tracks else None
        entry = db.insert_entry(mood, story_theme, activity_theme, music_summary)

        # also add to Chroma vectorstore
        if entry:
            vectormanager.add_mood_doc(
                mood_text=entry.mood_text,
                story_theme=entry.story_theme,
                activity_theme=entry.activity_theme,
                date_time=str(entry.date_time),
                uid=f"mood_{entry.mood_id}"
            )

# ----------------- RAG-enhanced Generation -----------------
if st.button("🔎 Generate (RAG)"):
    if not mood:
        st.warning("Please enter your mood.")
    else:
        parsed, retrieved = rag_generator.generate_with_rag(mood)
        st.subheader("📖 Story & Activities (RAG-enhanced)")
        if isinstance(parsed, dict) and "raw" not in parsed:
            st.markdown("**Story:**")
            st.write(parsed.get("story", ""))
            st.markdown("**Activities:**")
            for a in parsed.get("activities", []):
                st.write(f"- {a}")
            story_theme = parsed.get("story_theme") or (parsed.get("story", "").split(".")[0] if parsed.get("story") else "")
            activity_theme = parsed.get("activities", [None])[0] if parsed.get("activities") else None
            if st.button("Save this RAG result to history"):
                entry = db.insert_entry(mood, story_theme, activity_theme, None)
                if entry:
                    vectormanager.add_mood_doc(
                        mood_text=entry.mood_text,
                        story_theme=entry.story_theme,
                        activity_theme=entry.activity_theme,
                        date_time=str(entry.date_time),
                        uid=f"mood_{entry.mood_id}"
                    )
                st.success("Saved.")
        else:
            st.write(parsed.get("raw", str(parsed)))

        st.subheader("🗂 Retrieved Past Moods (context used)")
        if retrieved:
            for meta in retrieved:
                st.write(
                    f"{meta.get('date_time')} | Mood: {meta.get('mood_text')} | "
                    f"Story theme: {meta.get('story_theme')} | Activity: {meta.get('activity_theme')}"
                )
        else:
            st.info("No similar past moods found.")

# ----------------- Sidebar History -----------------
st.sidebar.title("📜 Mood History")
with st.sidebar.expander("⚙️ History Options", expanded=True):
    search_mood = st.text_input("🔍 Search by mood", "")
    limit = st.slider("Number of records", 5, 50, 10)

entries = db.fetch_entries(limit=limit)
if entries:
    for e in entries:
        if search_mood and search_mood.lower() not in e.mood_text.lower():
            continue
        with st.sidebar.expander(f"{e.date_time.strftime('%Y-%m-%d %H:%M')} | {e.mood_text}"):
            st.write(f"📖 Story Theme: {e.story_theme}")
            st.write(f"🎯 Activity Theme: {e.activity_theme}")
            if e.music_summary:
                st.write(f"🎵 Music summary: {e.music_summary}")
            if st.button(f"Regenerate for this mood: {e.mood_id}", key=f"reg_{e.mood_id}"):
                parsed, retrieved = rag_generator.generate_with_rag(e.mood_text)
                st.subheader("Revisited RAG story")
                st.write(parsed if parsed else "No result")
else:
    st.sidebar.info("No mood history yet.")
