import streamlit as st
from chains import overall_chain

st.title("MoodAI - Your Personal Mood Storyteller")

mood = st.text_input("How are you feeling today?", "")

if st.button("Generate Story & Activity"):
    if mood:
        results = overall_chain.invoke({"mood":mood})
        st.subheader("Story")
        st.write(results["story"])
        st.subheader("Activity Suggestion")
        st.write(results["activity"])
    else:
        st.warning("Please enter your mood.")

