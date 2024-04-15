from tkinter import ttk
import tkinter as tk
from PIL import ImageTk
from .score import Score


class Ac_icon:
	def __init__(self, frame, ac_value: Score) -> None:
		self._frame = frame
		self.ac = ac_value
		self._populate_ac_panel(ac_value.get_value())

	def _populate_ac_panel(self, ac_value):
		self.widgets = { 'frame': ttk.Frame(self._frame, width=75, height=75) }


		self.widgets['text_var'] =		tk.StringVar()
		self.widgets['text_var'].set(ac_value)
		
		#Load background image	
		self.widgets['img'] =			ImageTk.PhotoImage(file="media/images/icons/gui/icon_ac.png") 
		self.widgets['background'] =	tk.Label(self.widgets['frame'], image=self.widgets['img'])
		self.widgets['text'] =			tk.Label(self.widgets['frame'], textvariable=self.widgets['text_var'])

		#Update frame grid
		self.widgets['background'].place(x=0, y=0, relwidth=1, relheight=1)
		self.widgets['text'].place(relx=.5, rely=.4, anchor="center")
		

	def _populate_right_click_menu(self):
		self.right_click_menu = tk.Menu(self.widgets['frame'])

		self.possible_ac_status = [
			'Effect: Raise a Shield', # effect-raise-a-shield
			'Clumsy',
			'Off-Guard'
		]
		self.ac_options = self.possible_ac_status


	def _update_ac_options(self, options, remove = False, add = False):
		if remove == add:
			raise(ValueError('Invalid flags combinations!'))
		
		for option in options:
			if option in self.possible_ac_status:
				#Note that add means that the status has been added to the creature and thus needs be removed...
				if add:
					self.possible_ac_status.remove(option)
				elif remove:
					self.possible_ac_status.append(option)

	def reset_adjustments(self):
		self.ac.reset_adjustments()
		self.update_view()

	def update_view(self):
		total_value, modifier = self.ac.get_value(get_mod = True)
		
		#Update colour
		str_final_value = str(total_value)	

		if modifier:
			str_final_value += f"\n({'+' if modifier > 0 else ''}{modifier})"
			colour = 'green' if modifier > 0 else 'red'
		else:
			colour = 'black'
		self.widgets['text_var'].set(str_final_value)
		self.widgets['text'].configure(fg=colour)



	def add_mod(self, *kwargs):
		if self.ac.add_mod(*kwargs):
			self.update_view()
			
		# Update menu list