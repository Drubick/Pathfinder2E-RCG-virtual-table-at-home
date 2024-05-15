from  combat_generator.RCG_logic import *
from GUI import *
from tkinter import Tk
from GUI.Creature_selection import Item_search

if __name__ == "__main__":
	root = Tk()
	root.geometry('1000x800')
	app = Item_search(root)
	app._frame.pack(expand=True, fill='both')
	root.mainloop()