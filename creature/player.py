from bs4 import BeautifulSoup
from tkinter import ttk
from .statblock import Statblock

if __name__ == "__main__":
	from creature import Creature
	from score import Score
else:
	from .creature import Creature
	from .score import Score


class Player(Creature):
	def __init__(self, master, frame, iFrame, raw_data, add_level = True) -> None:
		
		self.player, self.monster = True, False

		#load name
		self.name =		raw_data['name']
		self._class =	raw_data['class']
		self.level =	raw_data['level']
		self.level_prof = raw_data['level'] if add_level else 0

		# Load base abilities
		self.cha =			Score((raw_data['abilities']['cha'] - 10) // 2)
		self.con =			Score((raw_data['abilities']['con'] - 10) // 2)
		self.dex =			Score((raw_data['abilities']['dex'] - 10) // 2)
		self.int =			Score((raw_data['abilities']['int'] - 10) // 2)
		self.wis =			Score((raw_data['abilities']['wis'] - 10) // 2)
		self.str =			Score((raw_data['abilities']['str'] - 10) // 2)

		#Load hp and ac
		max_hp = 10 + raw_data['attributes']['ancestryhp'] + self.con.get_value()
		if self.level > 1:
			max_hp +=  (self.level - 1) * (self.con.get_value() + raw_data['attributes']['classhp'] + raw_data['attributes']['bonushpPerLevel'])
		self.hp =			{
			'max': max_hp,
			'temp': 0,
			'value': Score(max_hp)
		}

		#Might be able to just use: raw_data['acTotal']['acTotal']?
		self.ac	=			Score(10 + raw_data['acTotal']['acProfBonus'] + raw_data['acTotal']['acAbilityBonus'] + raw_data['acTotal']['acItemBonus'])

		# Load immunities and resistances
		self.immunities =	[]
		self.resistances =	[]
		# TODO: Parse feats and ancestries...

		#Load saves
		saves_list = [
			('perception', None),
			('fortitude', self.con),
			('reflex', self.dex),
			('will', self.wis)
		]
		saves =	{key: Score(raw_data['proficiencies'][key] + self.level_prof, base_modifiers = mod) for key, mod in saves_list}
		self.perception =	saves['perception']
		del saves['perception']
		self.saves = {key: {'value': value, 'details': []} for key, value in saves.items()}
		#TODO: fill...
		self.all_saves = None

		self.allsaves =	[]

		#Load speed
		self.speed = Score(raw_data['attributes']['speed'] + raw_data['attributes']['speedBonus'])

		#Load traits
		self.alignment =	raw_data['alignment']
		self.senses =		[]
		self.languages =	raw_data['languages']
		self.traits =		[]
		#TODO: Add size modifiers...
		self.size =			raw_data['size']

		self.attacks = 		{
			'melee':	{},
			'ranged':	{}
		}
		self.load_skills(raw_data)
		self.equipment =	{}
		self.weapons =		{}
		#TODO: add armor penalizers
		self.armor =		{}
		self.consumables =	{}
		self.actions =		{}
		self.reactions =	{}
		self.passives =		{}


		#Load lore
		self.lore = 		[]


		super().__init__(master, frame, iFrame)

	def load_skills(self, raw_data):
		skills_map = {
			'acrobatics':	self.dex,
			'arcana':		self.int,
			'athletics':	self.str,
			'crafting':		self.int,
			'deception':	self.cha,
			'diplomacy':	self.cha,
			'intimidation':	self.cha,
			'lore':			self.int,
			'medicine':		self.wis,
			'nature':		self.wis,
			'occultism':	self.int,
			'performance':	self.cha,
			'religion':		self.wis,
			'society':		self.int,
			'stealth':		self.dex,
			'survival':		self.wis,
			'thievery':		self.dex
		}
		self.skills = {}

		for skill, prof_mod in skills_map.items():
			if skill in raw_data['proficiencies'] and raw_data['proficiencies'][skill]:
				self.skills[skill.capitalize()] = Score(raw_data['proficiencies'][skill] + self.level_prof, prof_mod)
				continue
			# If untrained don't add any modifiers
			self.skills[skill.capitalize()] = Score(0)

		# Add lore specific skills 
		for lore in raw_data['lores']:
			self.skills['Lore: ' + lore[0].capitalize()] =  Score(lore[1] + self.level_prof, prof_mod)
		pass