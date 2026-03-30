import requests
import time
import json
from pathlib import Path
from Anime_Add import AnimeApi


while True:
    valinta = input("Mitä haluat tehdä?: 1. Luo lista, 2. Lisää listaan, 3.Lue lista, 4.Poista listasta, 4.Poista lista, 0.Lopeta ohjelma ")
    print(valinta)
    kansio_tie = Path("Listat/")

############# Valinta 1 #############
    if valinta == "1": #or "Luo lista":
        uusi_lista_nimi = input("Anna listalle nimi: ('0' vie takaisin) ")
        if uusi_lista_nimi == "0":
            continue
        uusi_tie = Path(f"{kansio_tie}/{uusi_lista_nimi}.json")
        if not uusi_tie.exists():
            with open(uusi_tie, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

        continue

############# Valinta 2 #############  
    elif valinta == "2":
        for file in kansio_tie.glob("*.json"):
            print(file.name)
        avattava_lista_nimi = input("Lisättävän listan nimi? ('0' vie takaisin) ")
        if avattava_lista_nimi == "0":
            continue
# LISÄÄ TÄHÄN JOS TIEDOSTOA EI LÖYDY
        with open(f"{kansio_tie}/{avattava_lista_nimi}.json", "r", encoding="utf-8") as file:
            add_data_path = f"{kansio_tie}/{avattava_lista_nimi}.json"
        #print(data)
        animeinput = input('Anna Animen nimi? ')
        AnimeApi(animeinput, add_data_path)

        continue

  
############# Valinta 3 #############   
    elif valinta == "3":
        
        #kansio_tie = Path("Anime/")
        for file in kansio_tie.glob("*.json"):
            print(file.name)
        avattava_lista_nimi = input("Avattavan listan nimi? ('0' vie takaisin) ")
        if avattava_lista_nimi == "0":
            continue


        file_path = Path(f"{kansio_tie}/{avattava_lista_nimi}.json")

        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            print("Valitsemaasi tiedostoa ei ole olemassa.")
            data = {}

        if data:
            print("Listasta löytyy: ")
            for key in data.keys():
                print(f"- {key}")

            lista_valinta = input("Minkä haluaisit valita? ('0' vie takaisin) ")
            if lista_valinta == "0":
                continue
            if lista_valinta in data:
                print(json.dumps(data[lista_valinta], indent=2))
            else:
                print("valintaa ei listassa")
        else:
            print("ei valintaa listassa")

        continue


############# Valinta 4 #############
    elif valinta == "4":
        
        for file in kansio_tie.glob("*.json"):
            print(file.name)
        avattava_lista_nimi = input("Avattavan listan nimi? ('0' vie takaisin) ")
        if avattava_lista_nimi == "0":
            continue

        file_path = Path(f"{kansio_tie}/{avattava_lista_nimi}.json")

        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            print("Valitsemaasi tiedostoa ei ole olemassa")
            data = {}

        if data:
            print("Listasta löytyy")
            for key in data.keys():
                print(f"- {key}")

            remove_key = input("Minkä haluat poistaa?  ('0' vie takaisin) ")
            if remove_key == "0":
                continue
            if remove_key in data:
                del data[remove_key]

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"{remove_key} on poistettu.")
            else:
                print(f"{remove_key} nimistä ei löydy listalta")
        else:
            print("Tiedosto on tyhjä.")

############# Valinta 5 #############
    elif valinta == "5":
        for file in kansio_tie.glob("*.json"):
            print(file.name)
        avattava_lista_nimi = input("Poistettavan tiedoston nimi? ('0' vie takaisin) ")
        if avattava_lista_nimi == "0":
            continue
        poisto_vastaus = input(f"Oletko varma että haluat poistaa {avattava_lista_nimi}.json? (1: kyllä 2: ei) ")
        if poisto_vastaus == "2":
            continue
        else:
            file_path = Path(f"{kansio_tie}/{avattava_lista_nimi}.json")
            if file_path.exists():
                file_path.unlink()
                print("Tiedosto poistettu")
                continue
            else:
                print("tiedostoa ei ole olemassa")
                continue
        
############# Valinta 0 #############    
    elif valinta == "0":
        break

    else:
        print("Syöte väärä")
        continue