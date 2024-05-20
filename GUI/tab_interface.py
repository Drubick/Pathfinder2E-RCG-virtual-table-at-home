from tkinter import ttk 
from GUI import *
from GUI.Creature_selection import Item_search
from GUI.encounterMode import EncounterMode
from database.bestiary_database	import Database
from GUI.map import Map


#TODO ADD PLAYERS TO THE ENCOUNTER
class Tabs_interface:
    def __init__(self, root):
        
        self._frame = ttk.Frame(root)
        self._database = Database()
        self._frame.pack(expand=True, fill='both')
        self._notebook = ttk.Notebook(self._frame)
        
        #tab1 this will allow to select a list of monsters or generat a random encounter.
        #TODO ADD A CLKEAR ALL BUTTON
        #TODO SEPARAT THE MONSTER LIST IN 2 LISTS
        #FIRST LIST WILL BE A LIST WITH POTETIANL MONSTERS FOR THE ENCOUNTER
        #SECOND LIST IS THE FINAL LIST OF THE ENCOUNTER
        #THE SECOND LIST IS DPLSAYED IN A WIDGET THAT ALLOW TO CHANGE THE MONSTER TO WEAK OR ELITE
        #ADD A TREATH LEVEL IN THE WIDGET OF THE SECOND LIST THAT DISPLAYS THE THREAT ALL THE TIME
        #EVERYTIME I CLICK ON A MONSTER FROM THE FIRST LIST I ADD IT TO THE MONSTER OF THE SECOND LIST
        #A BUTTON TO DELETE A MONSTER FROM THE SECOND LIST
        #TODO ADD AN OPTION TO CHANGE THE NAME OF A MONSTER

        self.tab1 = ttk.Frame(self._notebook)
        self._notebook.add(self.tab1, text='Tab 1')
        self._creature_selection = Item_search(self.tab1)
        #tab2 this will display all of the monster stats and allow to add them to the encounter
        #TODO ADD PLAYERS TO ENCOUNTER
        #TODO ADD A CLEAR ALL BUTTON
        #TODO ADD A SCROLLBAR TO THE CREATURES FRAME
        self.tab2 = ttk.Frame(self._notebook)
        self._notebook.add(self.tab2, text='Tab 2')
        self._encounter_mode = EncounterMode(self.tab2, self._database)
        #tab3 this will allow to create a map and add tokens to it
        #TODO CREATE A BUTTON TO ADD A GENERIC ICON FOR EACH MONSTER GENERATED
        #TODO "sleeper monster" IT IS INVISIBLE UNTIL NOT SLEEP AND THEN IT APPEARS, SKIPS THE INITIATIVE
        #TODO ADD SEPARATE TOKENS THAT REPRESENT ENVIROMENT (FIRE, WATER, DOORS, HAZARDS.)
        #TODO IF A TOKEN HAS A DESCRIPTION TEXT SHOW IT IF THE SHOW TEXT BUTTON IS PRESSED ABOVE IT
        #TODO??  A WAY TO PREGENERATE AND SAVE A MAP FOR LATER USES OPENING IT IN A NEW TAB???
        self.tab3 = ttk.Frame(self._notebook)
        self._notebook.add(self.tab3, text='Tab 3')
        self._map = Map(self.tab3,  self._creature_selection._monster_list)
       
        self._notebook.pack(expand=True, fill='both')
        self._notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        
        #notebook widget
    def on_tab_changed(self, event):
        selected_tab_index = self._notebook.index(self._notebook.select())
        if selected_tab_index == 2:
            self._map._monster_list = self._creature_selection._monster_list
            self._map.draw_grid()
            self._map.refresh_monster_interface()
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
