from tkinter import ttk 

#This class will create a blank grid map or blank map,
#the user can import a map image from a file.
#The user can also add tokens to the map.
#the tokens can be linked via a database to a monster.
class Map:
    def __init__(self, root):
        self._frame = ttk.Frame(root)
        self._frame.pack(expand=True, fill='both')

        