import requests
import time
import json
from pathlib import Path


#animeinput = input('Anna Animen nimi? ')



def AnimeApi(animetitle, add_data_path):
    animetitle = animetitle
    add_data_path = add_data_path
    new_dict = {}
    base_url = "https://api.jikan.moe"
    
    response = requests.get(url=base_url+'/v4/anime', params={'q': animetitle, 'limit': 10})
    time.sleep(1)

    if response.status_code == 200:
        data = response.json()

        results = data["data"]

        for i, anime in enumerate(results):
            print(f"{i+1}. {anime['title']} ({anime['year']})")
        while True:
            choice2 = int(input("Valitse oikean Animen numero: (0 vie takaisin)"))
            if choice2 < 0 or choice2 > 5:
                print("valitse oikea numero 1- 5")
                continue
            elif choice2 == 0:
                return
            else:
                break
        choice = choice2 -1
        selected = results[choice]

        #print("Title:", selected["title"])
        #print("Episodes:", selected["episodes"])
        #print("Status:", selected["status"])
        #print("Aired:", selected["aired"]["string"])
        #print("Duration:", selected["duration"])
        #print("Synopsis:", selected["synopsis"])

        keys_to_copy = ["title", "episodes", "status", "aired", "duration", "synopsis"]
        chosen_anime_title = str(selected["title"])
        for key in keys_to_copy:
            if key == "aired":
                new_dict[key] = selected[key]["string"]
            else:
                new_dict[key] = selected[key]


        #print(type(selected))
        #new_dict.update(selected["title"])

        #print(new_dict)
        key = chosen_anime_title

        with open(f"{add_data_path}", "r") as f:
            data = json.load(f)

        data[key] = new_dict

        with open(f"{add_data_path}", "w") as f:
            json.dump(data, f, indent=2)


        #path = Path(f"{add_data_path}")
        #path.parent.mkdir(parents=True, exist_ok=True)



        #with path.open("w") as file:
        #    json.dump(new_dict, file, indent=4)

            #'small_image_url'
    else:
        print("API request failed")
        exit(1)



#AnimeApi(animeinput)