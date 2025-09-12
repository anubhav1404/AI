import streamlit as st
from database import insert_entry, fetch_entries
from chains import overall_chain

st.title("MoodAI - Your Personal Mood Storyteller")

mood = st.text_input("How are you feeling today?", "")

if st.button("Generate Story & Activity"):
    if mood:
        results = overall_chain.invoke({"mood": mood})
        
        # Show full story and activity
        st.subheader("Your Story")
        st.write(results["story"])
        st.subheader("Suggested Activity")
        st.write(results["activity"])
        
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






