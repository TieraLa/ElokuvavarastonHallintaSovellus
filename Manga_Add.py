import requests
import time
from PyQt6.QtWidgets import QInputDialog

def fetch_manga_data(mangatitle, parent=None):
    
    base_url = "https://api.jikan.moe"
    try:
        response = requests.get(base_url + "/v4/manga", params={"q": mangatitle, "limit": 10})
        time.sleep(1)  
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"API request failed: {e}")

    results = response.json().get("data", [])
    if not results:
        raise Exception("No results found")

    
    items = []
    for manga in results:
        published = manga.get("published", {})
        from_date = published.get("from")

        if from_date:
            year = from_date[:4]
        else:
            year = "?"

        items.append(f"{manga['title']} ({year})")

    
    
    choice, ok = QInputDialog.getItem(parent, "Select Manga", "Choose the correct manga:", items, 0, False)
    if not ok:
        return None  

    
    selected = results[items.index(choice)]

   
    published = selected.get("published", {})
    from_date = published.get("from", "")[:10]
    to_date = published.get("to")

    if to_date:
        to_date = to_date[:10]
    else:
        to_date = "Ongoing"

    manga_dict = {
        "title": f"{selected.get('title', '')} ({year}, {selected.get('type', '')})",
        "type": selected.get("type", ""),
        "chapters": selected.get("chapters", ""),
        "status": selected.get("status", ""),
        "published": f"{from_date} → {to_date}",
        "volumes": selected.get("volumes", ""),
        "synopsis": selected.get("synopsis", "")
    }

    return manga_dict