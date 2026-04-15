from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.uic import loadUi
import sys
import requests
import time
import json
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtWidgets import QDialog
from Anime_Add import fetch_anime_data

kansio_tie = Path("Listat/")

class AddYourDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("NewListWindow.ui", self)

        self.pushButton_add.clicked.connect(self.accept)
        self.pushButton_cancel.clicked.connect(self.reject)
        self.pushButton_autoAdd.clicked.connect(self.auto_fill_fields)

    def get_data(self):
        return {
            "title": self.lineEdit_title.text(),
            "episodes": self.parse_episodes(),
            "status": self.lineEdit_status.text(),
            "aired": self.lineEdit_aired.text(),
            "duration": self.lineEdit_duration.text(),
            "synopsis": self.lineEdit_synopsis.text()
        }

    def parse_episodes(self):
        text = self.lineEdit_episodes.text()
        return int(text) if text.isdigit() else None

    def auto_fill_fields(self):
        title_input = self.lineEdit_title.text().strip()
        if not title_input:
            QMessageBox.warning(self, "Error", "Please enter a title first!")
            return

        try:
            anime_data = fetch_anime_data(title_input, parent=self)
        except Exception as e:
            QMessageBox.warning(self, "API Error", str(e))
            return

        if not anime_data:
            return

        
        self.lineEdit_title.setText(anime_data.get("title", ""))
        self.lineEdit_episodes.setText(str(anime_data.get("episodes", "")))
        self.lineEdit_status.setText(anime_data.get("status", ""))
        self.lineEdit_aired.setText(anime_data.get("aired", ""))
        self.lineEdit_duration.setText(anime_data.get("duration", ""))
        self.lineEdit_synopsis.setText(anime_data.get("synopsis", ""))





class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        loadUi("Gui_Main.ui", self)

        self.pushButton_createnewlist.clicked.connect(self.addList)
        self.lineEdit_NewList.setText("New list name")
        self.listWidget_files.itemClicked.connect(self.load_json_titles)
        self.listWidget_titles.itemClicked.connect(self.show_anime_details)
        self.pushButton_removeList.clicked.connect(self.remove_list)
        self.pushButton_addNewEntry.clicked.connect(self.open_add_dialog)
        self.pushButton_remove.clicked.connect(self.remove_entry)
        self.pushButton_search.clicked.connect(self.search_all_lists)
        self.populate_file_list()
   
    def populate_file_list(self):
        self.listWidget_files.clear()

        for file in kansio_tie.glob("*.json"):
            display_name = file.stem  # 🔥 no .json

            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, file.name)  

            self.listWidget_files.addItem(item)

    def clear_details(self):
        self.textEdit_title.clear()
        self.textEdit_episodes.clear()
        self.textEdit_status.clear()
        self.textEdit_aired.clear()
        self.textEdit_duration.clear()
        self.textEdit_synopsis.clear()
        self.textEdit_fileLocation.clear()



    def load_json_titles(self, item):
        file_name = item.data(Qt.ItemDataRole.UserRole)
        self.current_file_path = kansio_tie / file_name

        with open(self.current_file_path, "r", encoding="utf-8") as f:
            self.current_data = json.load(f)

        self.listWidget_titles.clear()

        for title in self.current_data.keys():
            self.listWidget_titles.addItem(title)

        self.clear_details()
    

    def show_anime_details(self, item):
        data_role = item.data(Qt.ItemDataRole.UserRole)

        # If coming from search (tuple)
        if isinstance(data_role, tuple):
            title, file_name = data_role
            file_path = kansio_tie / file_name

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            anime = data.get(title, {})
            self.current_file_path = file_path
            self.current_data = data

        else:
            
            title = item.text()
            anime = self.current_data.get(title, {})

        self.textEdit_title.setPlainText(f"Title:\n{anime.get('title', '')}")
        self.textEdit_episodes.setPlainText(f"Episodes:\n{anime.get('episodes', '')}")
        self.textEdit_status.setPlainText(f"Status:\n{anime.get('status', '')}")
        self.textEdit_aired.setPlainText(f"Aired:\n{anime.get('aired', '')}")
        self.textEdit_duration.setPlainText(f"Duration:\n{anime.get('duration', '')}")
        self.textEdit_synopsis.setPlainText(f"Synopsis:\n{anime.get('synopsis', '')}")
        self.textEdit_fileLocation.setPlainText(f"List:\n{self.current_file_path.stem}")


    

    def addList(self):
        uusi_lista_nimi = self.lineEdit_NewList.text()
        uusi_tie = Path(f"{kansio_tie}/{uusi_lista_nimi}.json")
        
        if not uusi_tie.exists():
            with open(uusi_tie, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            self.populate_file_list()


    def remove_list(self):
        from PyQt6.QtWidgets import QMessageBox

        selected_item = self.listWidget_files.currentItem()

        if not selected_item:
            print("No file selected")
            return

        file_name = selected_item.data(Qt.ItemDataRole.UserRole)
        file_path = kansio_tie / file_name

        if not file_path.exists():
            print("File does not exist")
            return

       
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{file_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            file_path.unlink()
            print(f"Deleted: {file_name}")

            
            self.populate_file_list()
            self.listWidget_titles.clear()
            self.clear_details()


    def open_add_dialog(self):
        if not hasattr(self, "current_file_path"):
            QMessageBox.warning(self, "Error", "Select a list first!")
            return

        dialog = AddYourDialog()


        if dialog.exec(): 
            new_entry = dialog.get_data()
            title_key = new_entry["title"]

            if not title_key:
                print("Title is required")
                return

            
            with open(self.current_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            
            data[title_key] = new_entry

            
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            
            self.load_json_titles(self.listWidget_files.currentItem())


    def remove_entry(self):
        if not hasattr(self, "current_file_path"):
            QMessageBox.warning(self, "Error", "Select a list first!")
            return


        selected_item = self.listWidget_titles.currentItem()

        if not selected_item:
            QMessageBox.warning(self, "Error", "Select an entry to remove!")
            return

        title = selected_item.text()

        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        
        with open(self.current_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        
        if title in data:
            del data[title]

        
        with open(self.current_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        
        self.load_json_titles(self.listWidget_files.currentItem())

        self.clear_details()


    def search_all_lists(self):
        search_text = self.lineEdit_searchBar.text().strip().lower()

        if not search_text:
            QMessageBox.warning(self, "Error", "Enter a search term!")
            return

        self.listWidget_titles.clear()
        self.clear_details()

        results = []

        for file in kansio_tie.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading {file}: {e}")
                continue

            for title, info in data.items():
                # Combine all searchable fields
                searchable_text = " ".join([
                    str(info.get("title", "")),
                    str(info.get("episodes", "")),
                    str(info.get("status", "")),
                    str(info.get("aired", "")),
                    str(info.get("duration", "")),
                    str(info.get("synopsis", ""))
                ]).lower()

                if search_text in searchable_text:
                    results.append((title, file.name))

        
        for title, file_name in results:
            item = QListWidgetItem(f"{title} ({file_name})")
            item.setData(Qt.ItemDataRole.UserRole, (title, file_name))
            self.listWidget_titles.addItem(item)

        if not results:
            QMessageBox.information(self, "No Results", "No matches found.")





if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
