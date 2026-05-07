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
from Manga_Add import fetch_manga_data
from Book_Add import fetch_book_data

kansio_tie = Path("Listat/")


#----- CODE FOR THE ADD MENU WINDOW ------
class AddYourDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("NewListWindow.ui", self)

        self.pushButton_add.clicked.connect(self.try_accept)
        self.pushButton_cancel.clicked.connect(self.reject)
        self.pushButton_autoAdd.clicked.connect(self.auto_fill_fields)
        self.pushButton_clear.clicked.connect(self.clear_fields)
        self.edit_mode = False
        self.original_title = None

    #---WHEN EDITING WHAT IS LOADED FROM THE JSON---
    def load_data(self, data):
        self.lineEdit_title.setText(data.get("title", ""))
        self.lineEdit_type.setText(data.get("type", ""))
        self.lineEdit_status.setText(data.get("status", ""))
        self.lineEdit_episodes.setText(str(data.get("episodes", "")))
        self.lineEdit_chapters.setText(str(data.get("chapters", "")))
        self.lineEdit_volumes.setText(str(data.get("volumes", "")))
        self.lineEdit_aired.setText(data.get("aired", ""))
        self.lineEdit_duration.setText(data.get("duration", ""))
        self.lineEdit_synopsis.setText(data.get("synopsis", ""))
        self.lineEdit_owned.setText(data.get("owned", ""))
        self.lineEdit_pages.setText(str(data.get("pages", "")))

    def clear_fields(self):
        self.lineEdit_title.clear()
        self.lineEdit_status.clear()
        self.lineEdit_episodes.clear()
        self.lineEdit_chapters.clear()
        self.lineEdit_volumes.clear()
        self.lineEdit_aired.clear()
        self.lineEdit_duration.clear()
        self.lineEdit_synopsis.clear()
        self.lineEdit_type.clear()
        self.lineEdit_owned.clear()
        self.lineEdit_pages.clear()
        

    def get_data(self):
        return {
            "title": self.lineEdit_title.text(),
            "type": self.lineEdit_type.text(),
            "episodes": self.parse_episodes(),
            "status": self.lineEdit_status.text(),
            "chapters": self.parse_chapters(),
            "volumes": self.parse_volumes(),
            "aired": self.lineEdit_aired.text(),
            "duration": self.lineEdit_duration.text(),
            "synopsis": self.lineEdit_synopsis.text(),
            "owned": self.lineEdit_owned.text(),
            "pages": self.parse_pages() 
        }

    def parse_episodes(self):
        text = self.lineEdit_episodes.text()
        return int(text) if text.isdigit() else None

    def parse_chapters(self):
        text = self.lineEdit_chapters.text()
        return int(text) if text.isdigit() else None

    def parse_volumes(self):
        text = self.lineEdit_volumes.text()
        return int(text) if text.isdigit() else None

    def parse_pages(self):
        text = self.lineEdit_pages.text()
        return int(text) if text.isdigit() else None

    #---MAIN CODE FOR USING THE DIFFERENT APIS TO AUTOMATICALLY FILL THE FIELDS, ACTUAL API CODE IN DIFFERENT PYTHON FILES---
    def auto_fill_fields(self):
        title_input = self.lineEdit_title.text().strip()
        if not title_input:
            QMessageBox.warning(self, "Error", "Please enter a title first!")
            return

        selected_type = self.comboBox_type.currentText()

        try:
            if selected_type == "Anime":
                data = fetch_anime_data(title_input, parent=self)
            elif selected_type == "Manga":
                data = fetch_manga_data(title_input, parent=self)
            elif selected_type == "Book":
                data = fetch_book_data(title_input, parent=self)
            else:
                QMessageBox.warning(self, "Error", "Unknown type selected!")
                return
        except Exception as e:
            QMessageBox.warning(self, "API Error", str(e))
            return

        if not data:
            return

        #---WHAT ALL THE APIS MAINLY RETURN FROM THE AUTO ADD FUNCTION 
        self.lineEdit_title.setText(data.get("title", ""))
        self.lineEdit_type.setText(data.get("type", ""))
        self.lineEdit_status.setText(data.get("status", ""))
        self.lineEdit_aired.setText(data.get("aired") or data.get("published", ""))
        self.lineEdit_synopsis.setText(data.get("synopsis", ""))

        #--WHAT THE ANIME_ADD CODE RETURNS SPECIFICALLY
        if selected_type == "Anime":
            self.lineEdit_episodes.setText(str(data.get("episodes", "")))
            self.lineEdit_duration.setText(data.get("duration", ""))
            self.lineEdit_chapters.clear()
            self.lineEdit_volumes.clear()

        #--WHAT THE MANGA_ADD CODE RETURNS SPECIFICALLY
        elif selected_type == "Manga":
            self.lineEdit_chapters.setText(str(data.get("chapters", "")))
            self.lineEdit_volumes.setText(str(data.get("volumes", "")))
            self.lineEdit_episodes.clear()
            self.lineEdit_duration.clear()

            self.lineEdit_aired.setText(data.get("published", ""))

        #--WHAT THE BOOK_ADD CODE RETURNS SPECIFICALLY
        elif selected_type == "Book":
            self.lineEdit_type.setText("Book")

            
            self.lineEdit_episodes.clear()
            self.lineEdit_chapters.clear()
            self.lineEdit_volumes.clear()
            self.lineEdit_duration.clear()

            
            self.lineEdit_aired.setText(data.get("published", ""))
            self.lineEdit_pages.setText(str(data.get("pages") or ""))



    def try_accept(self):
        title = self.lineEdit_title.text().strip()

        if not title:
            QMessageBox.warning(self, "Error", "Title is required!")
            return

        
        parent = self.parent()
        data = {}

        if parent and hasattr(parent, "current_file_path"):
            try:
                with open(parent.current_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = {}

            
            if self.edit_mode:
                if title != self.original_title and title in data:
                    QMessageBox.warning(
                        self,
                        "Duplicate Entry",
                        f"An entry named '{title}' already exists!"
                    )
                    return
            else:
                if title in data:
                    QMessageBox.warning(
                        self,
                        "Duplicate Entry",
                        f"An entry named '{title}' already exists!"
                    )
                    return

        
        self.accept()




#----- CODE FOR THE MAIN WINDOW -----
class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        loadUi("Gui_Main.ui", self)

        self.pushButton_createnewlist.clicked.connect(self.addList)
        self.lineEdit_NewList.setPlaceholderText("New list name")
        self.listWidget_files.itemClicked.connect(self.load_json_titles)
        self.listWidget_titles.itemClicked.connect(self.show_anime_details)
        self.pushButton_removeList.clicked.connect(self.remove_list)
        self.pushButton_addNewEntry.clicked.connect(self.open_add_dialog)
        self.pushButton_remove.clicked.connect(self.remove_entry)
        self.pushButton_search.clicked.connect(self.search_all_lists)
        self.populate_file_list()
        self.pushButton_exit.clicked.connect(self.close)
        self.lineEdit_NewList.returnPressed.connect(self.addList)
        self.pushButton_edit.clicked.connect(self.edit_entry)
   
    def populate_file_list(self):
        self.listWidget_files.clear()

        for file in kansio_tie.glob("*.json"):
            display_name = file.stem  

            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, file.name)  

            self.listWidget_files.addItem(item)
    
    #--CLEARS THE INPUT FIELDS WHEN ADDING NEW ENTRY--- 
    def clear_details(self):
        self.textEdit_title.clear()
        self.textEdit_episodes.clear()
        self.textEdit_status.clear()
        self.textEdit_aired.clear()
        self.textEdit_duration.clear()
        self.textEdit_synopsis.clear()
        self.textEdit_fileLocation.clear()
        self.textEdit_chapters.clear()
        self.textEdit_volumes.clear()
        self.textEdit_type.clear()
        self.textEdit_owned.clear()
        self.textEdit_pages.clear()


    #--LOADS SELECTED JSON
    def load_json_titles(self, item):
        file_name = item.data(Qt.ItemDataRole.UserRole)
        self.current_file_path = kansio_tie / file_name

        with open(self.current_file_path, "r", encoding="utf-8") as f:
            self.current_data = json.load(f)

        self.listWidget_titles.clear()

        for title in self.current_data.keys():
            self.listWidget_titles.addItem(title)

        self.clear_details()
    
    #--SHOWS CONTENT OF JSON
    def show_anime_details(self, item):
        data_role = item.data(Qt.ItemDataRole.UserRole)

        
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
        self.textEdit_type.setPlainText(f"Type:\n{anime.get('type', '')}")
        self.textEdit_episodes.setPlainText(f"Episodes:\n{anime.get('episodes') or ''}")
        self.textEdit_status.setPlainText(f"Status:\n{anime.get('status', '')}")
        self.textEdit_aired.setPlainText(f"Aired:\n{anime.get('aired', '')}")
        self.textEdit_duration.setPlainText(f"Duration:\n{anime.get('duration', '')}")
        self.textEdit_synopsis.setPlainText(f"Synopsis:\n{anime.get('synopsis', '')}")
        self.textEdit_fileLocation.setPlainText(f"List:\n{self.current_file_path.stem}")
        self.textEdit_chapters.setPlainText(f"Chapters:\n{anime.get('chapters') or ''}")
        self.textEdit_volumes.setPlainText(f"Volumes:\n{anime.get('volumes') or ''}")
        self.textEdit_owned.setPlainText(f"Owned:\n{anime.get('owned', '')}")
        self.textEdit_pages.setPlainText(f"Pages:\n{anime.get('pages') or ''}")


    
    #--CODE FOR ADDING A NEW JSON FILE, CHECKS IF LIST NAME IS EMPTY AND GIVES ERROR--
    def addList(self):
        uusi_lista_nimi = self.lineEdit_NewList.text().strip()

        if not uusi_lista_nimi:
            QMessageBox.warning(self, "Error", "List name cannot be empty!")
            return

        uusi_tie = Path(f"{kansio_tie}/{uusi_lista_nimi}.json")

        if not uusi_tie.exists():
            with open(uusi_tie, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

            self.populate_file_list()
    
    #--CODE FOR REMOVING A JSON FILE--
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

    #-- CODE FOR ADDING NEW ENTRY TO A LIST, CHECKS IF LIST IS SELECTED FIRST--
    def open_add_dialog(self):
        if not hasattr(self, "current_file_path"):
            QMessageBox.warning(self, "Error", "Select a list first!")
            return

        dialog = AddYourDialog(self)


        if dialog.exec(): 
            new_entry = dialog.get_data()
            title_key = new_entry["title"].strip()

            if not title_key:
                QMessageBox.warning(self, "Error", "Title is required!")
                return

            with open(self.current_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            
            data[title_key] = new_entry

            
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            
            self.load_json_titles(self.listWidget_files.currentItem())

    #-- CODE FOR REMOVING  ENTRY TO A LIST, CHECKS IF ENTRY IS SELECTED FIRST--
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

    #-- SEARCH FUNCTION FOR SEARCHIN ALL THE JSON FILES FOR THE GIVEN KEYWORD--
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
                
                searchable_text = " ".join([
                    str(info.get("title", "")),
                    str(info.get("type", "")),
                    str(info.get("episodes", "")),
                    str(info.get("chapters", "")),
                    str(info.get("volumes", "")),
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


    #--CODE FOR EDITIGN AN EXISTING ENTRY--
    def edit_entry(self):
        selected_item = self.listWidget_titles.currentItem()

        if not selected_item:
            QMessageBox.warning(self, "Error", "Select an entry first!")
            return

        title = selected_item.text()

        with open(self.current_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        entry_data = data.get(title)
        if not entry_data:
            QMessageBox.warning(self, "Error", "Entry not found!")
            return

        dialog = AddYourDialog(self)

        
        dialog.edit_mode = True
        dialog.original_title = title

        
        dialog.load_data(entry_data)

        if dialog.exec():
            updated_data = dialog.get_data()

            with open(self.current_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            
            new_title = updated_data["title"].strip()

            
            if new_title != dialog.original_title and new_title in data:
                QMessageBox.warning(
                    self,
                    "Duplicate Entry",
                    f"An entry named '{new_title}' already exists!"
                )
                return

            
            if dialog.original_title != new_title:
                del data[dialog.original_title]

            data[new_title] = updated_data

            with open(self.current_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.load_json_titles(self.listWidget_files.currentItem())



#--THIS IS NEEDED TO RUN THE GUI--

if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
