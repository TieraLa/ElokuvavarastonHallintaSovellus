import requests
import time


#-- WHAT API IS UDES TO GET THE DATA---
#-- SEARCH FUNCTION THAT RETURNS LIST OF 10 ENTRIES BASED ON THE TITLE WORD
def fetch_anime_data(animetitle, parent=None):
    
    base_url = "https://api.jikan.moe"      #--WHAT API SITE IS USED

    try:
        response = requests.get(base_url + "/v4/anime", params={"q": animetitle, "limit": 10})
        time.sleep(1)  #-- MAKES SURE THE API SERVER IS NOT FLOODED WITH REQUESTS TOO MUCH
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

    #--SELECT CORRECT ANIME
    from PyQt6.QtWidgets import QInputDialog
    choice, ok = QInputDialog.getItem(parent, "Select Anime", "Choose the correct anime:", items, 0, False)
    if not ok:
        return None  

    
    selected = results[items.index(choice)]

   
    aired = selected.get("aired", {})
    from_date = aired.get("from", "")[:10]
    to_date = aired.get("to")

    if to_date:
        to_date = to_date[:10]
    else:
        to_date = "Ongoing"
    
    #-- WHAT IS RETURNED TO THE MAIN CODE --
    anime_dict = {
        "title": f"{selected.get('title', '')} ({selected.get('year', '')}, {selected.get('type', '')})",
        "type": selected.get("type", ""),
        "episodes": selected.get("episodes", ""),
        "status": selected.get("status", ""),
        "aired": f"{from_date} → {to_date}",
        "duration": selected.get("duration", ""),
        "synopsis": selected.get("synopsis", "")
    }

    return anime_dict