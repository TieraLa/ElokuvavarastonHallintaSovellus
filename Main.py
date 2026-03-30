from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.uic import loadUi
import sys
import requests
import time
import json
from pathlib import Path

kansio_tie = Path("Listat/")

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        loadUi("Gui_Main.ui", self)

        self.pushButton_createnewlist.clicked.connect(self.addList)
        self.lineEdit_NewList.setText("New list name")
        self.listWidget_files.itemClicked.connect(self.load_json_titles)
        self.listWidget_titles.itemClicked.connect(self.show_anime_details)

        self.populate_file_list()
   
    def populate_file_list(self):
        self.listWidget_files.clear()

        for file in kansio_tie.glob("*.json"):
            self.listWidget_files.addItem(file.name)

    def clear_details(self):
        self.textEdit_title.clear()
        self.textEdit_episodes.clear()
        self.textEdit_status.clear()
        self.textEdit_aired.clear()
        self.textEdit_duration.clear()
        self.textEdit_synopsis.clear()




    def load_json_titles(self, item):
        file_name = item.text()
        self.current_file_path = kansio_tie / file_name

        with open(self.current_file_path, "r", encoding="utf-8") as f:
            self.current_data = json.load(f)

        self.listWidget_titles.clear()

        for title in self.current_data.keys():
            self.listWidget_titles.addItem(title)

        self.clear_details()
    

    def show_anime_details(self, item):
        title = item.text()
        data = self.current_data.get(title, {})

        # Fill each field safely
        self.textEdit_title.setPlainText(
            f"Title:\n{data.get('title', '')}"
        )

        self.textEdit_episodes.setPlainText(
            f"Episodes:\n{data.get('episodes', '')}"
        )

        self.textEdit_status.setPlainText(
            f"Status:\n{data.get('status', '')}"
        )

        self.textEdit_aired.setPlainText(
            f"Aired:\n{data.get('aired', '')}"
        )

        self.textEdit_duration.setPlainText(
            f"Duration:\n{data.get('duration', '')}"
        )

        self.textEdit_synopsis.setPlainText(
            f"Synopsis:\n{data.get('synopsis', '')}"
        )


    

    def addList(self):
        uusi_lista_nimi = self.lineEdit_NewList.text()
        uusi_tie = Path(f"{kansio_tie}/{uusi_lista_nimi}.json")
        
        if not uusi_tie.exists():
            with open(uusi_tie, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            self.populate_file_list()  # 🔥 refresh UI





    def addList(self):
        uusi_lista_nimi = self.lineEdit_NewList.text()
        uusi_tie = Path(f"{kansio_tie}/{uusi_lista_nimi}.json")
        
        if not uusi_tie.exists():
            with open(uusi_tie, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
