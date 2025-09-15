import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
DEFAULT_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Music_icon.png/600px-Music_icon.png"

# ----------------- Mood + Language Mapping -----------------
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
    "Hindi": "bollywood",   # bollywood is stronger than "hindi"
    "Punjabi": "bhangra",
    "Spanish": "latin",
    "K-Pop": "kpop",
    "Any": None
}

# ----------------- Helpers -----------------
def _format_number_like(n):
    """Format numeric-looking strings like '10543' -> '10,543'. Return raw if not numeric."""
    try:
        i = int(str(n).replace(",", ""))
        return f"{i:,}"
    except Exception:
        return str(n)


def _extract_listeners(track):
    """
    Try several possible fields where Last.fm might keep listener/playcount.
    Returns pretty string or 'N/A' if not available.
    """
    # direct fields
    for key in ("listeners", "playcount"):
        val = track.get(key)
        if val:
            return _format_number_like(val)

    # sometimes nested under 'stats' or '@attr'
    if isinstance(track.get("stats"), dict):
        val = track["stats"].get("listeners") or track["stats"].get("playcount")
        if val:
            return _format_number_like(val)
    if isinstance(track.get("@attr"), dict):
        val = track["@attr"].get("listeners") or track["@attr"].get("playcount")
        if val:
            return _format_number_like(val)

    # Some track.search returns 'listeners' as '0' or missing — final fallback
    return "N/A"


def _extract_artist_name(track):
    artist = track.get("artist")
    if isinstance(artist, dict):
        return artist.get("name", "Unknown Artist")
    elif artist:
        return str(artist)
    # sometimes search returns 'artist' nested differently
    if isinstance(track.get("artist"), str):
        return track.get("artist")
    # fallback
    return "Unknown Artist"


def _extract_image(track):
    if "image" in track and track["image"]:
        # Last item often largest
        try:
            img = track["image"][-1].get("#text") or track["image"][-1].get("text")
            if img:
                return img
        except Exception:
            pass
    return DEFAULT_IMAGE


# ----------------- Main function -----------------
def get_music_recommendation(mood: str, language: str = "Any", limit: int = 5):
    """
    Returns (recommendations_list, used_tag)
    - recommendations_list: list of tracks (title, artist, url, listeners, image, mood, language)
    - used_tag: the tag that returned results (for diagnostics), or None
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    mood_tag = MOOD_TAGS.get(mood, mood.lower().strip())
    language_tag = LANGUAGE_TAGS.get(language, None)

    # Candidate tags (priority order): mood+lang -> lang -> mood -> pop
    candidates = []
    if language_tag:
        candidates.append(f"{mood_tag} {language_tag}")  # e.g., "romantic bollywood"
        candidates.append(language_tag)                 # e.g., "bollywood"
    candidates.append(mood_tag)
    candidates.append("pop")

    for tag in candidates:
        params = {
            "method": "tag.gettoptracks",
            "tag": tag,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": limit * 2,  # fetch extra so we can filter duplicates/junk
        }
        try:
            resp = requests.get(url, params=params, timeout=8)
        except Exception:
            continue
        if resp.status_code != 200:
            continue
        data = resp.json()
        tracks = data.get("tracks", {}).get("track", [])
        if not tracks:
            continue

        # Format + filter out junk (like playlist-like entries)
        recs = []
        seen = set()
        for t in tracks:
            title = t.get("name") or t.get("title") or t.get("trackName")
            artist_name = _extract_artist_name(t)
            if not title or not artist_name:
                continue
            # skip obvious playlist/compilation labels
            if "playlist" in str(title).lower() or "various" in str(artist_name).lower():
                continue
            key = (title.strip().lower(), artist_name.strip().lower())
            if key in seen:
                continue
            seen.add(key)

            recs.append({
                "title": title,
                "artist": artist_name,
                "url": t.get("url", "#"),
                "listeners": _extract_listeners(t),
                "image": _extract_image(t),
                "mood": mood,
                "language": language
            })
            if len(recs) >= limit:
                break

        if recs:
            return recs, tag  # success, return tag used

    # nothing found
    return [], None
