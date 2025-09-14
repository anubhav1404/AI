import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

def get_music_recommendation(mood: str, limit: int = 3):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": mood,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        tracks = data.get("tracks", {}).get("track", [])
        recommendations = []
        for track in tracks:
            recommendations.append({
                "name": track["name"],
                "artist": track["artist"]["name"],
                "url": track["url"],   # link to listen
                "listeners": track.get("listeners", "N/A"),
                "image": track["image"][-1]["#text"] if track.get("image") else None
            })
        return recommendations
    return []
