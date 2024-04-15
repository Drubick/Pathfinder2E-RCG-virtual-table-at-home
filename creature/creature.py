from tkinter import ttk
import tkinter as tk
from infoFrame import infoFrame, SlideFrame
from .modifier_holder import Modifier
from .statblock import Statblock

if __name__ == "__main__":
	from ac_icon import Ac_icon
else:
	from .ac_icon import Ac_icon
import random

class Creature():
	def __init__(self, master, frame, infoFrame) -> None:
		self._frame = ttk.Frame(frame)
		self._encounterHandler = master
		self._infoFrame = infoFrame

		self.nameVar = tk.StringVar(value=self.name)
		self._nameLabel = ttk.Label(self._frame, textvariable=self.nameVar, width=40, anchor='center',)
		self._populate_health()
		self._populate_saves()
		self.status_effects = []
		self._populate_buttons()
		self._ac_rep = Ac_icon(self._frame, self.ac)
		self.initiative =	''
		self.index =		0
		self.adjustment =	'normal'

		#Render the various elements
		self._frame.grid_rowconfigure(0, weight=1)
		self._nameLabel.grid(				column=1, row=0, padx=5)
		self._hp_bar.grid(					column=0, row=1, padx=5, pady=5, columnspan=2)
		self._saves_rep['frame'].grid(		column=3, row=0, columnspan=2, rowspan=3, padx=5, pady=5)
		self._ac_rep.widgets['frame'].grid(	column=6, row=0, columnspan=2, rowspan=2, padx=5, pady=5)
		self.button_frame.grid(row=3, column=0, columnspan=4, pady=10)
		for i, button in enumerate(self.buttons):
			button.grid(column = i + 1, row = 0, padx=5)
	
	def get_statblock(self):
		return Statblock(self._infoFrame, len(self._infoFrame._infoFrames), self)

	def show_statblock(self):
		self._infoFrame.add_info_slide(slide = self.get_statblock())

	def _get_health_adjustment(self):
		health_adjustment = {
			1:	10,
			4:	15,
			19: 20,
		}

		for threshold, value in health_adjustment.items():
			if self.level <= threshold:
				return value
		return 30
	
	def handle_creature_adjust(self, event):
		adjustment = self.buttons[0].get()
		health_change = self._get_health_adjustment()
	
		# Always reset to normal (unless it' already normal)
		if self.adjustment != 'Normal':
			health_change = health_change if self.adjustment == 'Weak' else -health_change
			self._change_max_health(health_change)
			self.reset_adjustment_modifiers()
		
		self.adjustment = adjustment
		if adjustment != 'Normal':
			# Adjust to the required level
			self.set_adjustment_modifiers(-2 if adjustment == 'Weak' else +2, adjustment)
			self._change_max_health(health_change)

	def reset_adjustment_modifiers(self):
		for score in self.get_adjustment_scores():
			score.reset_adjustments()

	def set_adjustment_modifiers(self, modifier, name):
		for score in self.get_adjustment_scores():
			score.add_mod(modifier, name, '', 'balance')

	def get_adjustment_scores(self):
		adjustment_modifiers = [
			self._ac_rep,
			self.ac,
			self.str,
			self.cha,
			self.con,
			self.dex,
			self.int,
			self.cha,
			self.wis,
			self.perception
		]
		#Todo: add spell modifiers and attack rolls
		return adjustment_modifiers

	def delete(self):
		self._encounterHandler.remove_creature(self.index)
		
	def _populate_buttons(self):
		self.button_frame = tk.Frame(self._frame)
		self.buttons = [
			ttk.Combobox(self.button_frame, state='readonly', values = ['Weak', 'Normal', 'Elite']),
			ttk.Button(self.button_frame, text='Statblock', command=self.show_statblock),
			ttk.Button(self.button_frame, text='Remove', command=self.delete)
		]
		self.buttons[0].bind("<<ComboboxSelected>>", self.handle_creature_adjust)
		self.buttons[0].set('Normal')

	def _populate_health(self):
		self.current_health = tk.IntVar()
		self.current_health.set(self.hp['max'])
		self._hp_bar = ttk.Progressbar(
			self._frame,
			maximum=self.hp['max'],
			orient='horizontal',
			mode='determinate',
			value=self.hp['max'],
			variable=self.current_health,
			length=30*10
		)

	def _populate_saves(self):
		self._saves_rep = { 'frame': ttk.Frame(self._frame, width=150, height=75) }
		i = 0
		saves = self.saves
		saves['perception'] = {'value': self.perception}
		for key, value in saves.items():
			self._saves_rep[key] = Modifier(self._saves_rep['frame'], value['value'].total_value, key[:4].capitalize())
			self._saves_rep[key]._frame.pack()

	def change_name(self, new_name):
		self.nameVar.set(new_name)

	def _change_max_health(self, health_change):
		self.hp['max'] += health_change
		self._hp_bar['maximum'] = self.hp['max']
		self.change_health(health_change)

	def change_health(self, value):
		current_health = self.current_health.get()
		if current_health + value < 0:
			current_health = 0
		elif current_health + value > self.hp['max']:
			current_health = self.hp['max']
		else:
			current_health += value
		self.current_health.set(current_health)
		self.hp['value'] = current_health

	def set_save_mod(self, type, **kwargs):
		
		#Update internal value
		if type == 'perception':
			self.perception.add_mod(*kwargs)
		elif type in self.saves:
			self.saves[type]['value'].add_mod(*kwargs)
		else:
			return

	def roll_init(self, score = None):
		base_roll = random.random() * 20 // 1

		if score:
			if score in self.skills:
				bonus = self.skills[score]['value'] + self.skills[score]['mod']
			else:
				bonus = 0
		else:
			bonus = self.perception['value'] + self.perception['mod']

		return base_roll + bonus
	
# 	Weak Adjustments
# Source Bestiary pg. 6
# Sometimes you’ll want a creature that’s weaker than normal so you can use a creature that would otherwise be too challenging, or show that one enemy is weaker than its kin. To do this quickly and easily, apply the weak adjustments to its statistics as follows.

# * Decrease the creature’s AC, attack modifiers, DCs, saving throws, and skill modifiers by 2.
# * Decrease the damage of its Strikes and other offensive abilities by 2. If the creature has limits on how many times or how often it can use an ability (such as a spellcaster’s spells or a dragon’s Breath Weapon), decrease the damage by 4 instead.
# * Decrease the creature’s HP based on its starting level.

# Weak Adjustment
# 
# Starting Level	HP Decrease
# 1-2	-10
# 3-5	-15
# 6-20	-20
# 21+	-30



# https://stackoverflow.com/questions/13510882/how-to-change-ttk-progressbar-color-in-python