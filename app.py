import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain
from music import get_music_recommendation   # <-- new import

st.title("MoodAI - Your Personal Mood Storyteller")

mood = st.text_input("How are you feeling today?", "")

# Supported languages
languages = ["Any", "English", "Hindi", "Punjabi", "Spanish", "K-Pop"]

# Dropdown for language selection
song_lang = st.selectbox("Preferred Music Language 🎵", languages, index=0)

if st.button("Generate Story, Activity & Music"):
    if mood:
        results = overall_chain.invoke({"mood": mood})
        
        # Show full story and activity
        st.subheader("Your Story")
        st.write(results["story"])
        st.subheader("Suggested Activity")
        st.write(results["activity"])

        # 🎵 Music Recommendation
        st.subheader("Music Recommendation")

        if song_lang == "Any":
            for lang in languages[1:]:  # skip "Any"
                st.markdown(f"### 🎶 {lang}")
                music_list = get_music_recommendation(mood, lang)

                if music_list and len(music_list) > 0:
                    track = music_list[0]  # take top track
                    st.markdown(f"🎵 **[{track['title']}]({track['url']})** by *{track['artist']}*")
                    st.write(f"👥 Listeners: {track['listeners']}")
                    if track["image"]:
                        st.image(track["image"], width=150)
                else:
                    st.write("No music found for this category.")
                st.markdown("---")
        else:
            music_list = get_music_recommendation(mood, song_lang)
            if music_list:
                for track in music_list[:5]:  # show top 5 songs for selected lang
                    st.markdown(f"🎵 **[{track['title']}]({track['url']})** by *{track['artist']}*")
                    st.write(f"👥 Listeners: {track['listeners']}")
                    if track["image"]:
                        st.image(track["image"], width=150)
                    st.markdown("---")
            else:
                st.write("No music found for this mood and language.")

        # Extract short themes
        story_theme = results["story"].split(".")[0]
        activity_theme = results["activity"].split(",")[0]
        
        # Save themes to DB
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
