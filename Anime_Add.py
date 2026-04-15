import requests
import time

def fetch_anime_data(animetitle, parent=None):
    
    base_url = "https://api.jikan.moe"
    try:
        response = requests.get(base_url + "/v4/anime", params={"q": animetitle, "limit": 10})
        time.sleep(1)  
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"API request failed: {e}")

    results = response.json().get("data", [])
    if not results:
        raise Exception("No results found")

    
    items = []
    for anime in results:
        year = anime.get("year", "?")
        items.append(f"{anime['title']} ({year})")

    
    from PyQt6.QtWidgets import QInputDialog
    choice, ok = QInputDialog.getItem(parent, "Select Anime", "Choose the correct anime:", items, 0, False)
    if not ok:
        return None  

    
    selected = results[items.index(choice)]

   
    keys_to_copy = ["title", "episodes", "status", "aired", "duration", "synopsis"]
    anime_dict = {}
    for key in keys_to_copy:
        if key == "aired":
            anime_dict[key] = selected[key]["string"] if selected.get(key) else ""
        else:
            anime_dict[key] = selected.get(key, "")

    return anime_dict