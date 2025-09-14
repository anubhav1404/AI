import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain
from music import get_music_recommendation

st.title("🎭 MoodAI - Your Personal Mood Storyteller + Music")

mood = st.text_input("💭 How are you feeling today?", "")

language = st.selectbox(
    "🎶 Choose your music language",
    ["Any", "English", "Hindi", "Punjabi", "Spanish", "K-Pop"],
    index=0
)

if st.button("✨ Generate Story, Activity & Music"):
    if mood:
        results = overall_chain.invoke({"mood": mood})

        # Story + Activity
        st.subheader("📖 Your Story")
        st.write(results["story"])
        st.subheader("🎯 Suggested Activity")
        st.write(results["activity"])

        # Music
        st.subheader(f"🎶 Music Recommendation ({language})")
        music_list = get_music_recommendation(mood, language)

        music_summary = None
        if music_list:
            for idx, track in enumerate(music_list):
                st.markdown(f"**[{track['title']}]({track['url']})** by *{track['artist']}*")
                st.write(f"👥 Listeners: {track['listeners']}")
                st.image(track["image"], width=120)
                st.markdown("---")

                if idx == 0:  # Save first song as summary
                    music_summary = f"{track['title']} - {track['artist']}"
        else:
            st.write("⚠️ No music found for this mood + language.")

        # Save short versions in DB
        story_theme = results["story"].split(".")[0]
        activity_theme = results["activity"].split(",")[0]
        insert_entry(mood, story_theme.strip(), activity_theme.strip(), music_summary)

    else:
        st.warning("⚠️ Please enter your mood.")

# History
st.subheader("🕒 Mood History (Recent)")
entries = fetch_entries(limit=10)
for entry in entries:
    st.write(f"📅 {entry.date_time.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"💭 Mood: {entry.mood_text}")
    st.write(f"📖 Story: {entry.story_theme}")
    st.write(f"🎯 Activity: {entry.activity_theme}")
    if entry.music_summary:
        st.write(f"🎶 Music: {entry.music_summary}")
    st.markdown("---")
