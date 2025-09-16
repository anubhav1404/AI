# music.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
DEFAULT_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Music_icon.png/600px-Music_icon.png"

MOOD_TAGS = {
    "Happy": "happy",
    "Sad": "sad",
    "Romantic": "romantic",
    "Chill": "chill",
    "Energetic": "energetic",
    "Party": "party",
    "Workout": "workout",
    "Calm": "calm"
}

LANGUAGE_TAGS = {
    "English": "english",
    "Hindi": "bollywood",
    "Punjabi": "bhangra",
    "Spanish": "latin",
    "K-Pop": "kpop",
    "Any": None
}

class MusicRecommender:
    def __init__(self, api_key: str = LASTFM_API_KEY):
        self.api_key = api_key

    def _fetch_track_info(self, artist: str, title: str):
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "track.getInfo",
            "api_key": self.api_key,
            "artist": artist,
            "track": title,
            "format": "json"
        }
        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code == 200:
                return resp.json().get("track", {})
        except Exception:
            return {}
        return {}

    def _extract_image(self, track_info):
        if "album" in track_info and "image" in track_info["album"]:
            images = track_info["album"]["image"]
            if images:
                return images[-1].get("#text") or DEFAULT_IMAGE
        if "image" in track_info and track_info["image"]:
            return track_info["image"][-1].get("#text") or DEFAULT_IMAGE
        return DEFAULT_IMAGE

    def get_music_recommendation(self, mood: str, language: str = "Any", limit: int = 5):
        url = "http://ws.audioscrobbler.com/2.0/"
        mood_tag = MOOD_TAGS.get(mood, mood.lower().strip())
        language_tag = LANGUAGE_TAGS.get(language, None)

        candidates = []
        if language_tag:
            candidates.append(f"{mood_tag} {language_tag}")
            candidates.append(language_tag)
        candidates.append(mood_tag)
        candidates.append("pop")

        for tag in candidates:
            params = {
                "method": "tag.gettoptracks",
                "tag": tag,
                "api_key": self.api_key,
                "format": "json",
                "limit": limit,
            }
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code != 200:
                continue

            data = resp.json()
            tracks = data.get("tracks", {}).get("track", [])
            if not tracks:
                continue

            recs = []
            for t in tracks:
                title = t.get("name")
                artist = t.get("artist", {}).get("name") if isinstance(t.get("artist"), dict) else t.get("artist")
                url = t.get("url", "#")

                if not title or not artist:
                    continue

                # Enrich with track.getInfo
                info = self._fetch_track_info(artist, title)
                listeners = info.get("listeners") or info.get("playcount") or "N/A"
                image_url = self._extract_image(info)

                recs.append({
                    "title": title,
                    "artist": artist,
                    "url": url,
                    "listeners": f"{int(listeners):,}" if str(listeners).isdigit() else listeners,
                    "image": image_url,
                    "mood": mood,
                    "language": language
                })

                if len(recs) >= limit:
                    return recs, tag  # stop once we have enough

        return [], None
