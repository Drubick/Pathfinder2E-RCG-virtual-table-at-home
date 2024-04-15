from tkinter import *
from tkinter import ttk

class Modifier():
	def __init__(self, master, variable: StringVar, name = None, showMod = False) -> None:
		self._frame = ttk.Frame(master, width=150, height=75)
		self._nameLabel = Label(self._frame, text=name)
		self._valueLabel = Label(self._frame, textvariable=variable)
		self.showMod = showMod
		
		# Calculate initial value
		initial_value = variable.get()
		if self.showMod and (index := initial_value.find(' ')):
			initial_value = initial_value[:index]
		self._initial_value = int(initial_value)
		
		#Pack the saves in their respective position
		if name:
			self._nameLabel.grid(column=0, row=0, padx=5)
			self._valueLabel.grid(column=1, row=0, padx=5)
		else:
			self._valueLabel.grid(padx=5)

		variable.trace_add('write', lambda x,y,z: self._valueLabel.after(2, self.on_update))

	def on_update(self):
		colour = 'black'
		new_value = self._valueLabel['text']
		if self.showMod and (index := new_value.find(' ')):
			new_value = new_value[:index]
		new_value = int(new_value)

		if new_value != self._initial_value:
			colour = 'green' if new_value > self._initial_value else 'red'
		self._valueLabel.configure(fg=colour)