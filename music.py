import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

LANGUAGE_TAGS = {
    "English": "english",
    "Hindi": "hindi",
    "Punjabi": "punjabi",
    "Spanish": "spanish",
    "K-Pop": "kpop",
    "Any": None
}

DEFAULT_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Music_icon.png/600px-Music_icon.png"

def get_music_recommendation(mood: str, language: str = "Any", limit: int = 3):
    """
    Fetch music recommendations from Last.fm using mood + language.
    Falls back to tag-based tracks if search fails.
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    tag = LANGUAGE_TAGS.get(language, None)

    # ---- 1. Try search API (more dynamic results) ----
    search_params = {
        "method": "track.search",
        "track": f"{mood} {tag}" if tag else mood,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(url, params=search_params)

    if response.status_code == 200:
        data = response.json()
        tracks = data.get("results", {}).get("trackmatches", {}).get("track", [])
        if tracks:  # If search gave results
            return _format_tracks(tracks, language)

    # ---- 2. Fall back to tag.gettoptracks (static but reliable) ----
    fallback_params = {
        "method": "tag.gettoptracks",
        "tag": tag or "pop",  # default to "pop" if no tag
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    response = requests.get(url, params=fallback_params)
    if response.status_code == 200:
        data = response.json()
        tracks = data.get("tracks", {}).get("track", [])
        return _format_tracks(tracks, language)

    return []

def _format_tracks(tracks, language):
    """Helper to format track data safely."""
    recommendations = []
    for track in tracks:
        image_url = DEFAULT_IMAGE
        if "image" in track and track["image"]:
            image_url = track["image"][-1].get("#text") or DEFAULT_IMAGE

        artist_name = None
        if isinstance(track.get("artist"), dict):
            artist_name = track["artist"].get("name", "Unknown Artist")
        else:
            artist_name = track.get("artist", "Unknown Artist")

        recommendations.append({
            "title": track.get("name", "Unknown Title"),
            "artist": artist_name,
            "url": track.get("url", "#"),
            "listeners": track.get("listeners", "N/A"),
            "image": image_url,
            "language": language
        })
    return recommendations