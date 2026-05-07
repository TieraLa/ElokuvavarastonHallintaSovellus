import requests
import time
import re
from PyQt6.QtWidgets import QInputDialog


session = requests.Session()

_last_request_time = 0


#-- MAKES SURE THE API SERVER IS NOT FLOODED WITH REQUESTS TOO MUCH
def rate_limit():
    global _last_request_time
    now = time.time()
    wait = 1.0 - (now - _last_request_time)

    if wait > 0:
        time.sleep(wait)

    _last_request_time = time.time()

#-- WHAT API IS USED TO GET THE DATA---
#-- SEARCH FUNCTION THAT RETURNS LIST OF 10 ENTRIES BASED ON THE TITLE WORD
def fetch_book_data(booktitle, parent=None):
    search_url = "https://openlibrary.org/search.json"      #--WHAT API SITE IS USED

    
    try:
        rate_limit()
        response = session.get(search_url, params={"q": booktitle, "limit": 10})
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"API request failed: {e}")

    results = response.json().get("docs", [])
    if not results:
        raise Exception("No results found")

    
    items = []
    for book in results:
        title = book.get("title", "Unknown")
        author = ", ".join(book.get("author_name", [])) if book.get("author_name") else "Unknown"
        year = book.get("first_publish_year", "?")

        items.append(f"{title} - {author} ({year})")

    choice, ok = QInputDialog.getItem(
        parent,
        "Select Book",
        "Choose the correct book:",
        items,
        0,
        False
    )

    if not ok:
        return None

    selected = results[items.index(choice)]

    
    title = selected.get("title", "")
    authors = ", ".join(selected.get("author_name", [])) if selected.get("author_name") else "Unknown"
    year = selected.get("first_publish_year", "?")
    work_key = selected.get("key")

    display_title = f"{title} ({year}, {authors})"

    
    pages = ""

    edition_keys = selected.get("edition_key", [])

    #--GETS THE PAGE NUMBER FROM AN EDITION TOP FROM THE SEARCH LIST--
    if edition_keys:
        try:
            rate_limit()
            edition_id = edition_keys[0]
            edition_url = f"https://openlibrary.org/books/{edition_id}.json"        #--WHAT API SITE IS USED
            edition_resp = session.get(edition_url)
            edition_data = edition_resp.json()

            pages = edition_data.get("number_of_pages")

            
            if not pages:
                pagination = edition_data.get("pagination", "")
                if isinstance(pagination, str):
                    match = re.search(r"\d+", pagination)
                    if match:
                        pages = int(match.group())

        except Exception as e:
            print("Edition fetch failed:", e)

    #ALTERNATIVE TO GET PAGES
    if not pages and work_key:
        try:
            rate_limit()
            editions_url = f"https://openlibrary.org{work_key}/editions.json"       #--WHAT API SITE IS USED
            editions_resp = session.get(editions_url)
            editions_data = editions_resp.json()

            entries = editions_data.get("entries", [])

            for ed in entries:
                if ed.get("number_of_pages"):
                    pages = ed["number_of_pages"]
                    break

                pagination = ed.get("pagination")
                if isinstance(pagination, str):
                    match = re.search(r"\d+", pagination)
                    if match:
                        pages = int(match.group())
                        break

        except Exception as e:
            print("Work editions fetch failed:", e)

    
    synopsis = ""

    if work_key:
        try:
            rate_limit()
            work_url = f"https://openlibrary.org{work_key}.json"        #--WHAT API SITE IS USED
            work_resp = session.get(work_url)
            work_data = work_resp.json()

            desc = work_data.get("description")

            if isinstance(desc, dict):
                synopsis = desc.get("value", "")
            elif isinstance(desc, str):
                synopsis = desc

        except Exception as e:
            print("Synopsis fetch failed:", e)

    #--WHAT IS RETURNED TO THE MAIN CODE
    return {
        "title": display_title,
        "type": "Book",
        "author": authors,
        "pages": pages,
        "published": str(year),
        "status": "",
        "synopsis": synopsis
    }