from bs4 import BeautifulSoup
from pprint import pprint
import re

if __name__ == "__main__":
	from creature import Creature
	from score import Score
else:
	from .creature import Creature
	from .score import Score

class DatabaseCreature(Creature):
	def __init__(self, master, frame, iFrame, raw_data, add_level = True) -> None:
		
		self.player, self.monster = False, True

		#load name
		self.name = raw_data['name']
		self.level =		raw_data['system']['details']['level']['value']
		self.level_prof = self.level if add_level else 0

		#Load hp and ac
		self.hp =			raw_data['system']['attributes']['hp']
		self.ac	=			Score(raw_data['system']['attributes']['ac']['value'])
		# Load base abilities
		self.cha =			Score(raw_data['system']['abilities']['cha']['mod'])
		self.con =			Score(raw_data['system']['abilities']['con']['mod'])
		self.dex =			Score(raw_data['system']['abilities']['dex']['mod'])
		self.int =			Score(raw_data['system']['abilities']['int']['mod'])
		self.wis =			Score(raw_data['system']['abilities']['wis']['mod'])
		self.str =			Score(raw_data['system']['abilities']['str']['mod'])

		# Load immunities and resistances
		self.immunities =	[immunity['type'] for immunity in raw_data['system']['attributes'].get('immunities', [])]
		self.resistances =	raw_data['system']['attributes'].get('resistances', [])

		#Load saves
		saves_list = {
			'fortitude': self.con,
			'reflex': self.dex,
			'will': self.wis
		}
		self.saves = {}

		# The value of the database is 10 + proficiency + level + modifier.
		# Since we want to add the raw modifier value so it can change based on the modifier bonus
		# we have to get the value without that modifier.
		# Similarly, since we might want to play without adding the level, that value is also removed
		# (0 if there's a level mod -so no change-, else level)
		self.level_value = 0 if self.level_prof else self.level
		for save_name, related_score in saves_list.items():
			mod_value = related_score.get_value()
			self.saves[save_name] = raw_data['system']['saves'][save_name]
			self.saves[save_name]['value'] = Score(self.saves[save_name]['value'] - self.level_value - mod_value, related_score)

		self.all_saves =	raw_data['system']['attributes']['allSaves']['value']

		#Load speed
		self.speed =		Score(raw_data['system']['attributes']['speed']['value'])
		self.other_speeds = raw_data['system']['attributes']['speed']['otherSpeeds']

		self.perception =	Score(raw_data['system']['perception']['mod'])

		#Load traits
		self.senses =		raw_data['system']['perception']['senses']
		self.languages =	raw_data['system']['details']['languages']['value']
		self.traits =		raw_data['system']['traits']['value']
		self.size =			raw_data['system']['traits']['size']['value']

		self.attacks = 		{
			'melee':	{},
			'ranged':	{}
		}
		self.skills =		{}
		self.equipment =	{}
		self.weapons =		{}
		self.armor =		{}
		self.consumables =	{}
		self.actions =		{}
		self.reactions =	{}
		self.passives =		{}
		self.spells =		{}


		#Load lore
		self.lore = 		BeautifulSoup(raw_data['system']['details']['publicNotes'], 'html.parser').get_text('').strip('\n')

		#Load remaining json info
		self.load_json_items(raw_data['items'])

		super().__init__(master, frame, iFrame)


	def load_json_items(self, items_json):
		'''

			* spellcastingEntry: Holds the slots it has as well as the dc and such
			* spell
			* consumable
			* equipment
		'''

		skills_map = {
			'Acrobatics':	self.dex,
			'Arcana':		self.int,
			'Athletics':	self.str,
			'Crafting':		self.int,
			'Deception':	self.cha,
			'Diplomacy':	self.cha,
			'Intimidation':	self.cha,
			'Lore':			self.int,
			'Medicine':		self.wis,
			'Nature':		self.wis,
			'Occultism':	self.int,
			'Performance':	self.cha,
			'Religion':		self.wis,
			'Society':		self.int,
			'Stealth':		self.dex,
			'Survival':		self.wis,
			'Thievery':		self.dex
		}
	
		for item in items_json:
			if item['type'] in ['melee', 'ranged']:
				self.parse_json_attack(item)
			elif item['type'] == 'lore':
				self.parse_json_skill(item, skills_map)
			elif item['type'] == 'action':
				self.parse_json_action(item)
			elif item['type'] == 'weapon':
				self.parse_json_weapon(item)
			elif item['type'] == 'armor':
				self.parse_json_armor(item)
			elif item['type'] == 'consumable':
				self.parse_json_consumable(item)
			elif item['type'] == 'equipment':
				self.parse_json_equipment(item)
			elif item['type'] == 'spell':
				self.parse_json_spell(item)
			else:
				print(item['type'] + '; ' +  item['name'])
	
	def parse_json_skill(self, item, skills_map):
		skill_name =  item['name'] if 'Lore' not in item['name'] else 'Lore'
		skill_value =  skills_map[skill_name].get_value()
		value = item['system']['mod']['value'] - skill_value - self.level_value
		self.skills[item['name']] = Score(value, skills_map[skill_name])

	def _parse_dice(self, dice_string):
		'''
			Extracts the dice amount and type from the given dice string
		'''
		if (match := re.match(r'(?P<dice_amount>\d+)(?P<dice_type>d\d+)\s?(?:(?P<mod_kind>\+|-)\s?(?P<mod>\d?))?', dice_string)):
			return match.groupdict()
		raise(ValueError('Couldn\'t parse dice value!'))
	
	def _get_attack_bonus(self, attack):
		'''
			Returns a score object with the value of the given attack bonus.
			If the weapon has the finesse trait and the dex mod is bigger than the
			strength mod, the dex mod will be used. Otherwise it will use strength
		'''

		attack_bonus = attack['system']['bonus']['value']
		strength_mod = self.str.get_value()
	
		# Check if the dexterity mod is bigger than strength
		if 'finesse' in attack['system']['traits']['value']:
			dex_mod = self.dex.get_value()
			mod = self.dex if dex_mod > strength_mod else self.str
		else:
			mod = self.str
		return Score(attack_bonus - mod.get_value() - self.level_value, mod, show_signs=True)
		

	def parse_json_attack(self, item):
		# melee doesn't necessaryly mean melee attack, but rather, add strength to the attack
		if item['type'] == 'melee':
			attack_type = item['system']['weaponType']['value']
			# item['weaponType']['value'] == 'melee' or 'ranged'
			self.attacks[attack_type][item['name']] = {
				'bonus':			self._get_attack_bonus(item),
				'damageRolls':		[],
				'traits':			item['system'].get('traits', {'value':None})['value'],
				'attack-effects':	item['system']['attackEffects']
			}
			for damage_type in item['system']['damageRolls'].values():
				damage = self._parse_dice(damage_type['damage'])
				damage_type = damage_type['damageType']
				
				#Calculate the damage score
				damage_mod = int(damage['mod'] if damage['mod'] else 0)
				if damage['mod_kind'] != '+':
					damage_mod -= damage_mod

				damage_mod = Score(damage_mod - self.str.get_value() - self.level_value, self.str)
				self.attacks[attack_type][item['name']]['damageRolls'].append({
					'dice_amount':	Score(int(damage['dice_amount'])),
					'dice_type':	damage['dice_type'],
					'modifier':		damage_mod
				})
		else:
			#Not entirely sure if there are more types soooo...
			raise(ValueError('Unparsed attack type'))

	def parse_json_spell(self, item):
		casting_time = item['system']['time']['value']
		try:
			casting_time = int(casting_time)
		except:
			pass
		spell = { 'casting_time': casting_time }
		
		# Parse spell damage dices
		if item['system']['damage']:
			dices = []
			for damage in item['system']['damage'].values():
				damage_info = self._parse_dice(damage['formula'])
				damage_info['type'] = damage['type']
				dices.append(damage_info)
			spell['damage'] = dices

		# Add the traditions and traits
		description = [
			f'Traditions: {", ".join(item["system"]["traits"]["traditions"])}',
			f'\nTraits: {", ".join(item["system"]["traits"]["value"])}',
			f'\nTarget: {item["system"]["target"]["value"]}',
			f'\n\n' + item['system']['description']['value']
		]
		spell['description'] = '\n'.join(description)
		self.spells[item['name']] = spell


	def _get_runes(self, item):
		return {
			'potency_level':	item['system'].get('potencyRune', {'value':None})['value'],
			'property_rune_1': 	item['system'].get('propertyRune1', {'value':None})['value'],
            'property_rune_2': 	item['system'].get('propertyRune2', {'value':None})['value'],
            'property_rune_3': 	item['system'].get('propertyRune3', {'value':None})['value'],
            'property_rune_4': 	item['system'].get('propertyRune4', {'value':None})['value']
		}

	def parse_json_armor(self, item):
		self.armor[item['name']] = {
			'ac_bonus':			item['system']['acBonus'],
			'category':			item['system']['category'],
			'description':		BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n'),
			'dex_cap':			item['system']['dexCap'],
			'require_strength':	item['system']['strength'],
			'speed_penalty':	item['system']['speedPenalty'],
			'quantity':			item['system']['quantity'],
			'traits':			item['system'].get('traits', {'value':None})['value'],
			'usage':			item['system'].get('usage', {'value':None})['value'],
			'price':			item['system'].get('price', {'value':None})['value'],
			'runes':			self._get_runes(item)
		}

	def parse_json_weapon(self, item):
		self.weapons[item['name']] = {
			'damage':		item['system']['damage'],
			'description':	BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n'),
			'hp':			item['system']['hp']['max'],
			'quantity':		item['system']['quantity'],
			'traits':		item['system'].get('traits', {'value':None})['value'],
			'usage':		item['system'].get('usage', {'value':None})['value'],
			'price':		item['system'].get('price', {'value':None})['value'],
			'runes':		self._get_runes(item)
		}

	def parse_json_consumable(self, item):
		self.consumables[item['name']] = {
			'type':				item['system'].get('price', {'value':None})['value'],
			'quantity':			item['system']['quantity'],
			'description':		BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n'),
			'charges':			item['system'].get('charges', {'value':None})['value'],
			'consume':			item['system'].get('consume', {'value':None}),
			'quantity':			item['system']['quantity'],
			'traits':			item['system'].get('traits', {'value':None})['value'],
			'usage':			item['system'].get('usage', {'value':None})['value'],
			'price':			item['system']['price']['value']
		}

	def parse_json_equipment(self, item):
		self.equipment[item['name']] = {
			'quantity':			item['system']['quantity'],
			'description':		BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n'),
			'quantity':			item['system']['quantity'],
			'traits':			item['system'].get('traits', {'value':None})['value'],
			'usage':			item['system'].get('usage', {'value':None})['value'],
			'price':			item['system']['price']['value']
		}


	def parse_json_action(self, item):
		if item['system']['actionType']['value'] == 'passive':
			self.passives[item['name']] = BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n')
		elif item['system']['actionType']['value'] == 'reaction':
			self.reactions[item['name']] = BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n')
		elif item['system']['actionType']['value'] == 'action':
			self.actions[item['name']] = {
				'actions': item['system']['actions']['value'],
				'description': BeautifulSoup(item['system']['description']['value'], 'html.parser').get_text('').strip('\n')
			}
		else:
			print('Unparsed action: ', item['system']['actionType']['value'])

		# Attack type action image name, modifier (trait 1, trait 2); Damage xdx+attack modifier damage type
		# ability name (traits); action description

		# Special resistances
		# {
		#     "exceptions": [
		#         "adamantine",
		#         "bludgeoning"
		#     ],
		#     "type": "physical",
		#     "value": 6
		# }