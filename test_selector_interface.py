from  combat_generator.RCG_logic import *
from Selector import *
from tkinter import Tk
from Selector.Creature_selection import App

if __name__ == "__main__":
	root = Tk()
	root.geometry('1000x800')
	app = App(root)
	app._frame.pack(expand=True, fill='both')
	root.mainloop()