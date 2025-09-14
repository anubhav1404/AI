import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain
from music import get_music_recommendation   # <-- new import

st.title("MoodAI - Your Personal Mood Storyteller")

mood = st.text_input("How are you feeling today?", "")

if st.button("Generate Story, Activity & Music"):
    if mood:
        results = overall_chain.invoke({"mood": mood})
        
        # Show full story and activity
        st.subheader("Your Story")
        st.write(results["story"])
        st.subheader("Suggested Activity")
        st.write(results["activity"])

        # 🎵 Get music recommendation
        st.subheader("Music Recommendation")
        music_list = get_music_recommendation(mood)

        if music_list:
            for track in music_list:
                st.markdown(f"🎵 **[{track['name']}]({track['url']})** by *{track['artist']}*")
                st.write(f"👥 Listeners: {track['listeners']}")
                if track["image"]:
                    st.image(track["image"], width=150)
                st.markdown("---")
        else:
            st.write("No music found for this mood.")

        # Extract short themes
        story_theme = results["story"].split(".")[0]
        activity_theme = results["activity"].split(",")[0]
        
        # Save themes to DB (not saving music yet)
        insert_entry(mood, story_theme.strip(), activity_theme.strip())
    else:
        st.warning("Please enter your mood.")

# Show recent history
st.subheader("Mood History (Recent)")
entries = fetch_entries(limit=10)
for entry in entries:
    st.write(f"Date: {entry.date_time.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"Mood: {entry.mood_text}")
    st.write(f"Story: {entry.story_theme}")
    st.write(f"Activity: {entry.activity_theme}")
    st.markdown("---")  # separator line
