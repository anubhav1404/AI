import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain
from music import get_music_recommendation

st.set_page_config(page_title="MoodAI", layout="wide")

st.title("🎭 MoodAI - Your Personal Mood Storyteller")

# --- Main Input ---
mood = st.text_input("How are you feeling today?", "")

if st.button("Generate Story, Activity & Music"):
    if mood:
        results = overall_chain.invoke({"mood": mood})

        # Show full story and activity
        st.subheader("📖 Your Story")
        st.write(results["story"])
        st.subheader("🎯 Suggested Activity")
        st.write(results["activity"])

        # 🎵 Get music recommendation
        st.subheader("🎶 Music Recommendation")
        music_list = get_music_recommendation(mood)

        if music_list:
            for track in music_list:
                st.markdown(f"🎵 **[{track['title']}]({track['url']})** by *{track['artist']}*")
                st.write(f"👥 Listeners: {track['listeners']}")
                if track["image"]:
                    st.image(track["image"], width=150)
                st.markdown("---")
        else:
            st.write("No music found for this mood.")

        # Extract short themes
        story_theme = results["story"].split(".")[0]
        activity_theme = results["activity"].split(",")[0]

        # Save themes to DB
        insert_entry(mood, story_theme.strip(), activity_theme.strip())
    else:
        st.warning("Please enter your mood.")

# --- Sidebar: Mood History ---
st.sidebar.title("📜 Mood History")

# Controls
with st.sidebar.expander("⚙️ History Options", expanded=True):
    search_mood = st.text_input("🔍 Search by Mood", "")
    limit = st.slider("Number of records", min_value=5, max_value=50, value=10, step=5)

# Fetch entries
entries = fetch_entries(limit=limit)

if entries:
    st.sidebar.write("Click on a past mood to revisit it:")
    for entry in entries:
        if search_mood.lower() in entry.mood_text.lower():
            if st.sidebar.button(f"{entry.date_time.strftime('%Y-%m-%d %H:%M')} | {entry.mood_text}"):
                # Re-generate full details for this past mood
                results = overall_chain.invoke({"mood": entry.mood_text})

                st.subheader("📖 Revisited Story")
                st.write(results["story"])
                st.subheader("🎯 Revisited Activity")
                st.write(results["activity"])

                st.subheader("🎶 Music Recommendation (Revisited)")
                music_list = get_music_recommendation(entry.mood_text)
                if music_list:
                    for track in music_list:
                        st.markdown(f"🎵 **[{track['title']}]({track['url']})** by *{track['artist']}*")
                        st.write(f"👥 Listeners: {track['listeners']}")
                        if track["image"]:
                            st.image(track["image"], width=150)
                        st.markdown("---")
                else:
                    st.write("No music found for this mood.")
else:
    st.sidebar.info("No mood history yet.")
