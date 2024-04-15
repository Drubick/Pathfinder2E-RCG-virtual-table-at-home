import tkinter as tk
from tkinter import *
from infoFrame.TextFrame import TextFrame
from creature.score import Score


class Statblock(TextFrame):

	def __del__(self):

		#Removes the traces from all the scores
		for score_info in self.scores:
			score_info['score'].trace_remove('read', score_info['trace'])

	def __init__(self, info_frame, index, creature, font='Helvetica 12') -> None:
		# Parent constructor
		super().__init__(info_frame, index, [], font)
	
		self.scores = {}
		self.action_paths = {
			1:				'media/images/icons/gui/actions/action_single.png',
			2:				'media/images/icons/gui/actions/action_double.png',
			3:				'media/images/icons/gui/actions/action_triple.png',
			'reaction':		'media/images/icons/gui/actions/action_reaction.png',
			'separator':	'media/images/icons/gui/actions/separator.png'
		}
		self.action_imgs = {}
		self.creature = creature


		self.insert_normal_text(creature.name + '\n')

		self.insert_separator()

		if creature.monster:
			self.insert_normal_text(f'Recall Knowledge - {self.get_recall_knowledge()}\n')
			self.insert_separator()
		
		self.insert_score(self.creature.perception, name='Perception ', tags='bold')
		if self.creature.languages:
			self.insert_normal_text('\nLanguages: ', tags='bold')
			self.insert_normal_text(', '.join(self.creature.languages))
		self.insert_skills()
		self.insert_normal_text('\n\n')
		self.insert_ability_scores()
		#TODO: List items
		self.insert_separator()
		self.insert_score(self.creature.ac, name='AC ', tags='bold')
		self.insert_score(self.creature.saves['fortitude']['value'], name='; Fort ', tags='bold')
		self.insert_score(self.creature.saves['reflex']['value'], name='; Ref ', tags='bold')
		self.insert_score(self.creature.saves['will']['value'], name='; Will ', tags='bold')
		if self.creature.all_saves:
			self.insert_normal_text('; ' + self.creature.all_saves)
		self.insert_normal_text('\nHP ', tags='bold')
		self.insert_normal_text(str(self.creature.hp['max']) + '\n')
		self.insert_passive_actions()
		self.insert_separator()
		self.insert_score(self.creature.speed, name='Speed ', tags='bold')
		self.insert_spells()
		self.insert_attacks()
		self.insert_actions()
		self.insert_reactions()

		self.insert_separator()
		self.insert_clickable_text('Creature lore', self.creature.lore)

		# Add tags
		# Perception
		# Languages
		# Skills
		# Str Dex Con Int Wis, Cha
		# Items
		# Separator
		# AC Fort Ref, Will, remaining saves
		# Hp, healing notes
		# Passive actions
		# Separator
		# Speed
		# Attacks
		# abilites
		# reactions
		# Separator

	def insert_attacks(self):
		self.insert_normal_text('\nAttacks:\n', tags='bold_italic')
		for attack_type, attacks in self.creature.attacks.items():
			for attack_name, attack in attacks.items():
				self.insert_normal_text(f'\t{attack_type.capitalize()} ', tags='bold_italic')
				self.insert_icon(attack['actions'] if 'actions' in attack else 1)
				self.insert_normal_text(' ')

				#Insert the attack name
				if 'description' in attack:
					self.insert_clickable_text(attack_name, attack['description'])
				else:
					self.insert_normal_text(attack_name)

				self.insert_normal_text(' ')
				self.insert_score(attack['bonus'])
				self.insert_normal_text(f' ({", ".join(attack["traits"])})')

				self.insert_normal_text('\n')


	def insert_reactions(self):
		if self.creature.reactions:
			self.insert_normal_text('\nReactions:\n', tags='bold_italic')
			for reaction_name, reaction in self.creature.reactions.items():
				self.insert_normal_text('\t')
				self.insert_icon('reaction')
				self.insert_clickable_text(reaction_name, reaction)
				self.insert_normal_text('\n')

	def insert_actions(self):
		if self.creature.actions:
			self.insert_normal_text('\nActions:\n', tags='bold_italic')
			for action_name, action in self.creature.actions.items():
				self.insert_normal_text('\t')
				self.insert_icon(action['actions'])
				self.insert_clickable_text(action_name, action['description'])
				self.insert_normal_text('\n')
				

	def insert_passive_actions(self):
		for index, passive in enumerate(self.creature.passives):
			clean_passive = passive.replace('-', '').replace(' ', '')
			expanded_passive = self._parentFrame._database.extract_reference(self.creature.passives[passive])
			#Handles cases where the description is just the name of the passive
			if len(expanded_passive) == 3 and expanded_passive[1]['text'] == clean_passive:
				self.insert_clickable_text(passive, expanded_passive[1]['expandable'])
			elif len(expanded_passive) == 1:
				if expanded_passive[0]['text']:
					self.insert_clickable_text(passive, expanded_passive[0]['text'])
				else:
					#If the text is empty don't add clickable text
					self.insert_normal_text(passive)
			else:
				self.insert_clickable_text(passive, self.creature.passives[passive])
			if (index + 1 != len(self.creature.passives)):
				self.insert_normal_text(', ')

	def insert_skills(self):
		self.insert_normal_text('\nSkills:\n\t', tags='bold_italic')
		for index, skill_info in enumerate(self.creature.skills.items()):
			skill, score = skill_info
			self.insert_normal_text(skill + ' ')
			self.insert_score(score)
			if index + 1 != len(self.creature.skills):
				self.insert_normal_text(', ')

	def insert_spells(self):
		creature_spells = self.creature.spells

		if len(creature_spells):
			combat_spells =		{}
			non_combat_spells = {}

			self.insert_normal_text('\nSpells:\n', tags='bold_italic')
			for spell, spell_data in creature_spells.items():
				if spell_data['casting_time'] in self.action_paths:
					combat_spells[spell] = spell_data
				else:
					non_combat_spells[spell] = spell_data

			# Insert combat spells
			for spell, spell_data in combat_spells.items():
				self.insert_normal_text('\t')
				self.insert_icon(spell_data['casting_time'])
				self.insert_clickable_text(spell, spell_data['description'])
				self.insert_normal_text('\n')
			self.insert_normal_text('\n\tNon combat spells:\n', tags='italic')
		
			# Insert non combat spells
			for spell, spell_data in non_combat_spells.items():
				self.insert_normal_text('\t  * ')
				spell_data['description'] += f"\n\nCasting time: {spell_data['casting_time']}"
				self.insert_clickable_text(spell, spell_data['description'])
				self.insert_normal_text('\n')



	def insert_ability_scores(self):
		ability_scores = (
			('Str: ',	self.creature.str),
			(', Dex: ', self.creature.dex),
			(', Con: ', self.creature.con),
			(', Int: ', self.creature.int),
			(', Wis: ', self.creature.wis),
			(', Cha: ', self.creature.cha),
		)
		for ability_score in ability_scores:
			self.insert_score(ability_score[1], name=ability_score[0], tags='bold')

		self.insert_normal_text('\n')

	def insert_icon(self, action):
		'''
			Images need to remain referenced, otherwise the garbage collector destroys them
			Therefore, we first check if we have it already. Otherwise we load them to memory
			and then we use it in the text
		'''

		try:
			action = int(action)
		except ValueError:
			pass

		if action not in self.action_imgs:
			if action not in self.action_paths:
				raise ValueError(f'No image for the action \'{action}\'')
			self.action_imgs[action] = tk.PhotoImage(file = self.action_paths[action])
		self.insert_image(self.action_imgs[action])

	def update_score(self, index):
		if index in self.scores:
			score_range =  self._textWidget.tag_ranges(index)
			if not len(score_range):
				return
			score_start, score_end = score_range[0], score_range[1]

			#Removes the old text and tag info (on the text, the indexed tag remains unaffected)
			self._textWidget.tag_remove(index, score_start, score_end)
			self._textWidget.delete(score_start, score_end)
			
			#Inserts the new tag
			self.insert_score(self.scores[index]['score'], score_index=index, insert_index=score_start)

	def insert_score(self, score: Score,score_index = None, insert_index = END, name = None, tags = None):
		'''
			Inserts a score in the given position (defaults to last inserted character).
			A tag record is kept for all the inserted scores. That way, we can update
			the score info when the Score object is updated.
			
			If the tag info is not saved, it's added to the dictionary and a callback is set
				(Note that the callback is destroyed when the statblock is destroyed)
		'''

		if name:
			self.insert_normal_text(name, tags=tags)
		if not score_index:
			score_index = str(0 + len(self.scores))
		total_score, mods = score.get_value(get_mod=True)
		
		if not mods:
			colour = 'black'
		elif mods > 0:
			colour = 'green'
		else:
			colour = 'red'

		#Store the tab, if needed
		if score_index not in self.scores:
			self.scores[score_index] =  {
				'score':		score,
				'tag':			self._textWidget.tag_configure(score_index,  foreground=colour),
				'trace':		score.total_value.trace_add('write', lambda x,y,z: self._textWidget.after(2, self.update_score(score_index)))
			}
		else:
			self._textWidget.tag_configure(score_index, foreground=colour)
		
		#Insert the score
		self._textWidget.insert(insert_index, score.total_value.get(), score_index)

		

	def get_recall_knowledge(self):
		return ''
	
	def insert_separator(self):
		self.insert_icon('separator')
		self.insert_normal_text('\n')

	def test(self):
		self._textWidget.mark_set()
		self._textWidget.mark_gravity()