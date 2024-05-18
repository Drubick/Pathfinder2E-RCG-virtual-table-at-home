from GUI import *
from tkinter import Tk
from GUI.tab_interface import Tabs_interface

if __name__ == "__main__":
	root = Tk()
	root.geometry('1000x800')
	app = Tabs_interface(root)
	app._frame.pack(expand=True, fill='both')
	root.mainloop()