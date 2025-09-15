import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain
from music import get_music_recommendation

st.set_page_config(page_title="MoodAI", layout="wide")
st.title("🎭 MoodAI - Your Personal Mood Storyteller")

# --- Inputs ---
mood = st.text_input("💭 How are you feeling today?", "")

language = st.selectbox(
    "🎶 Choose music language",
    ["Any", "English", "Hindi", "Punjabi", "Spanish", "K-Pop"],
    index=0
)

if st.button("✨ Generate Story, Activity & Music"):
    if not mood:
        st.warning("Please enter your mood.")
    else:
        # Call LangChain/Bedrock chain
        results = overall_chain.invoke({"mood": mood})

        # Show story + activity
        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("📖 Your Story")
            st.markdown(f"<div style='padding:10px; background:#f7f7fb; border-radius:8px;'>{results.get('story','')}</div>", unsafe_allow_html=True)
        with col2:
            st.subheader("🎯 Suggested Activity")
            st.markdown(f"<div style='padding:10px; background:#f0ffef; border-radius:8px;'>{results.get('activity','')}</div>", unsafe_allow_html=True)

        # Music
        st.subheader("🎶 Music Recommendation")
        tracks, used_tag = get_music_recommendation(mood, language=language, limit=4)
        if used_tag:
            st.caption(f"Results sourced from Last.fm tag: `{used_tag}`")
        if tracks:
            cols = st.columns(len(tracks))
            for i, t in enumerate(tracks):
                with cols[i]:
                    st.image(t["image"], width=150)
                    st.markdown(f"**[{t['title']}]({t['url']})**")
                    st.caption(f"by {t['artist']}")
                    st.write(f"👥 Listeners: {t['listeners']}")
        else:
            st.info("No music found for this mood + language combination. Showing other suggestions may help.")

        # Save short themes to DB
        story_theme = results.get("story", "").split(".")[0].strip() if results.get("story") else ""
        activity_theme = results.get("activity", "").split(",")[0].strip() if results.get("activity") else ""
        # Save first track as music_summary if present
        music_summary = None
        if tracks:
            music_summary = f"{tracks[0]['title']} - {tracks[0]['artist']}"
        insert_entry(mood, story_theme, activity_theme, music_summary)

# Sidebar history with clickable re-generate buttons
st.sidebar.title("📜 Mood History")
with st.sidebar.expander("⚙️ History Options", expanded=True):
    search_mood = st.text_input("🔍 Search by mood (sidebar)", "")
    limit = st.slider("Number of records", min_value=5, max_value=50, value=10, step=5)

entries = fetch_entries(limit=limit)
if entries:
    st.sidebar.write("Click an entry to revisit:")
    for idx, e in enumerate(entries):
        if search_mood.strip().lower() and search_mood.strip().lower() not in e.mood_text.lower():
            continue
        if st.sidebar.button(f"{e.date_time.strftime('%Y-%m-%d %H:%M')} | {e.mood_text}", key=f"hist_{idx}"):
            # re-generate for this mood (using selected language from main page)
            results = overall_chain.invoke({"mood": e.mood_text})
            st.subheader("📖 Revisited Story")
            st.write(results.get("story",""))
            st.subheader("🎯 Revisited Activity")
            st.write(results.get("activity",""))
            st.subheader("🎶 Revisited Music")
            tracks, used_tag = get_music_recommendation(e.mood_text, language=language, limit=4)
            if used_tag:
                st.caption(f"Results sourced from Last.fm tag: `{used_tag}`")
            if tracks:
                for t in tracks:
                    st.markdown(f"**[{t['title']}]({t['url']})** by *{t['artist']}*")
                    st.write(f"👥 Listeners: {t['listeners']}")
                    st.image(t["image"], width=120)
                    st.markdown("---")
            else:
                st.write("No music found for this mood.")
else:
    st.sidebar.info("No mood history yet.")
