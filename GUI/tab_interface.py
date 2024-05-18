from tkinter import ttk 
from GUI import *
from GUI.Creature_selection import Item_search
from GUI.encounterMode import EncounterMode
from database.bestiary_database	import Database



class Tabs_interface:
    def __init__(self, root):
        self._frame = ttk.Frame(root)
        self._database = Database()
        self._frame.pack(expand=True, fill='both')
        self._notebook = ttk.Notebook(self._frame)
        #tab1
        self.tab1 = ttk.Frame(self._notebook)
        self._creature_selection = Item_search(self.tab1)
        #tab2
        self.tab2 = ttk.Frame(self._notebook)
       
        self._notebook.add(self.tab1, text='Tab 1')
        self._notebook.add(self.tab2, text='Tab 2')
        
        self._encounter_mode = EncounterMode(self.tab2, self._database)
        self._notebook.pack(expand=True, fill='both')

        self._notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        
        #notebook widget
    def on_tab_changed(self, event):
        selected_tab_index = self._notebook.index(self._notebook.select())
        if selected_tab_index == 1:  # tab indices are 0-based, so tab2 is at index 1
            self.add_database_monster()
        if selected_tab_index == 0:
            self._encounter_mode.clear()

    def add_database_monster(self):
        print(f"Monster list length: {len(self._creature_selection._monster_list)}")
        for monster in self._creature_selection._monster_list:
            print(f"Adding monster: {monster['name']}")
            self._encounter_mode.add_raw_monster(monster)
     

if __name__ == "__main__":
	root = ttk()
	root.geometry('1000x800')
	app = Tabs_interface(root)
	app._frame.pack(expand=True, fill='both')
	root.mainloop()
