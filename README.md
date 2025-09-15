# MoodAI – Mood-Based Playlist & Storyteller

## 📌 Overview
MoodAI is an AI-powered app that generates **stories, activities, and music recommendations** based on the user’s mood.  
It uses **AWS Bedrock (Claude via LangChain)** for story & activity generation, **Last.fm API** for music, and stores history in an **SQLite database**.  
The app is built with **Streamlit** and later will be containerized and deployed to **Kubernetes (EKS)**.

---

## ✅ Features Completed
1. **Story & Activity Generation**
   - Uses LangChain + AWS Bedrock (Claude) to create:
     - A short story reflecting the mood.
     - Suggested activities for the user.

2. **Database (SQLite)**
   - Stores mood history in `moodai.db` with:
     - `mood_text`
     - `story_theme`
     - `activity_theme`
     - `date_time`
   - Shows last 10 entries in the app.

3. **Music Recommendations (Last.fm API)**
   - Suggests tracks based on mood + optional language filter (English, Hindi, Punjabi, Spanish, K-Pop, Any).
   - Displays:
     - Track name (clickable link to Last.fm).
     - Artist name.
     - Listener count.
     - Album art.

---

## 🔜 Next Planned Steps
- **Mood Journaling**: Allow user to add personal notes with each mood entry.
- **Data Visualization**: Show charts (mood trends, frequency, activity categories).
- **Personalization**: Recommend music/activities based on user history.
- **UI Polish**: Better layout with Streamlit (cards, columns, etc.).
- **Deployment**:
  - Dockerize the app.
  - Deploy on Kubernetes (Amazon EKS).

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **AI Backend**: LangChain + AWS Bedrock (Claude)
- **Database**: SQLite (later can move to Postgres if persistence is needed)
- **Music API**: Last.fm
- **Deployment**: Docker + Kubernetes (EKS)

---

## 📂 Current Files
- `app.py` → Main Streamlit app
- `chains.py` → LangChain + Bedrock logic (story + activity chains)
- `database.py` → SQLite setup (SQLAlchemy ORM)
- `music.py` → Last.fm API integration
- `requirements.txt` → Python dependencies
- `.env` → AWS + Last.fm credentials

---

## 📝 Usage Flow
1. User enters mood in Streamlit UI.
2. Bedrock generates:
   - A story.
   - An activity suggestion.
3. Last.fm fetches:
   - Music recommendations for mood + language.
4. All results are shown in the app.
5. Short themes are stored in DB for history.

---

## 🚀 Future Ideas
- Spotify API integration for richer music data.
- Sentiment analysis on mood journal notes.
- AI-generated playlists (via LangChain + Last.fm/Spotify).
- Multi-user support with authentication.