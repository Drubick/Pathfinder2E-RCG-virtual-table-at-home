from tkinter import StringVar

class Score():
	def __init__(self, value, base_modifiers = None, show_mods = False, show_signs = False ) -> None:
		self.value =		value
		self.show_mods =	show_mods
		self.total_value =	StringVar(value=str(''))
		self._override =	None
		self.show_sign =	show_signs

		self.buffs = {
			'item': 		{},
			'cicumpstance': {},
			'status':		{},
			'balance':		{}
		}
		self.penalties = {
			'item': 		{},
			'cicumpstance': {},
			'status':		{},
			'balance':		{}
		}
		self.dependant_scores = []
		
		if base_modifiers:
			if isinstance(base_modifiers, list):
				self.base_modifiers = base_modifiers
			else:
				self.base_modifiers = [base_modifiers]
			for score in self.base_modifiers:
				score.add_dependant(self)
		else:
			self.base_modifiers = []

		self.update_value()

	def override(self,
			  value,
			  description,
			  name,
			  allow_mod: dict | None = None,
			  allow_base_scores: bool = False,
			  duration = None
	):
		self._override = {
			'value':				value,
			'description':			description,
			'name':					name,
			'allow_mod':			allow_mod,
			'duration':				duration,
			'allow_base_scores':	allow_base_scores
		}
		self.update_value()

	
	def add_dependant(self, score):
		self.dependant_scores.append(score)

	def add_dependency(self, score):
		self.base_modifiers.append(score)
		score.add_dependant(self)

	def update_value(self):
		total_value, total_mod_value = self.get_value(get_mod=True)
		updated_value = str(total_value)

		#Add + sign if needed
		if self.show_sign and not total_value < 0:
			updated_value = '+' + updated_value
	
		if self.show_mods and total_mod_value:
			updated_value += f" {'+' if total_mod_value > 0 else ''}{total_mod_value}"
		self.total_value.set(updated_value)
		for dependant_score in self.dependant_scores:
			dependant_score.update_value()

	def reset_adjustments(self):
		self.buffs['balance'] =		{}
		self.penalties['balance'] = {}
		self.update_value()

	def add_mod(self, modifier, name, description, type, duration = None, level = 1):
		mod_type_dict = self.buffs if modifier > 0 else self.penalties

		if name in mod_type_dict[type]:
			if mod_type_dict[type][name]['level'] < level:
				mod_type_dict[type][name]['level'] = level
			if mod_type_dict[type][name]['modifier'] < modifier:
				mod_type_dict[type][name]['modifier'] = modifier
			mod_type_dict[type][name]['disabled'] = False

			#Update the duration
			# Keep the new duration if either is not set, else, keep the new one
			current_mod_duration = mod_type_dict[type][name]['duration']
			if not duration or not current_mod_duration:
				mod_type_dict[type][name]['duration'] = duration
			else:
				mod_type_dict[type][name]['duration'] = duration if duration > current_mod_duration else current_mod_duration
			
			return False
		else:
			mod_type_dict[type][name] = {
				'description':	description,
				'duration':		duration,
				'level':		level,
				'modifier':		modifier,
				'disabled':		False
			}
		self.update_value()
		return True
	
	def step_next_round(self):
		modifiers = (self.buffs, self.penalties)

		updated_buffs = {}
		for modifier_key, modifier in self.buffs.items():
			updated_buffs[modifier_key] = {mod_key:mod for mod_key, mod in modifier.items() if (not mod['duration'] or mod['duration'] > 1)}
		self.buffs = updated_buffs
		self.update_value()
	
	def get_value(self, get_mod = False, get_all = False):
		'''
			Returns a tuple of the total value of the score + the total value of the modifiers + a dict of active modifiers
		'''

		active_mods = self.get_active_mods()
		total_mod_value 		= 0
		total_base_mod_value 	= 0

		# Get active modifiers
		for mod_type in active_mods.values():
			for mod in mod_type.values():
				total_mod_value += mod['modifier']
		
		# Get base modifiers
		for score in self.base_modifiers:
			score_value, mod = score.get_value(get_mod = True)
			total_base_mod_value += score_value

		if self._override:
			total_value = self._override['value'] + total_mod_value
			if self._override['allow_base_scores']:
				total_value += total_base_mod_value
		else:
			total_value = self.value + total_mod_value + total_base_mod_value
		if get_all:
			return total_value, total_mod_value, active_mods
		elif get_mod:
			return total_value, total_mod_value
		else:
			return total_value

	def get_active_mods(self):
		active_mods = {}
		modifiers = [
			('buffs',		self.buffs),
			('penalties',	self.penalties)
		]
		if self._override:
			active_mods['override'] = self._override
		
		if not self._override or self._override['allow_mods']:
			for modifier in modifiers:
				active_mods[modifier[0]] = {}

				for mod_type in modifier[1].values():
					biggest_mod_key = None
					for key, mod in mod_type.items():
						if not mod['disabled']:
							if not biggest_mod_key:
								biggest_mod_key = key
								biggest_mod = mod['modifier']
							elif mod['modifier'] >= biggest_mod:
								biggest_mod = mod['modifier']
								biggest_mod_key = key

					if biggest_mod_key:
						active_mods[modifier[0]][biggest_mod_key] = mod_type[biggest_mod_key]
				
		return active_mods

	def disable_mod(self, name):
		'''
			Enables a modifier if disabled. Returns whether the modifier was changed
			(True would mean that the buff has changed and so the gui needs updating...)
		'''
		for mod_type in [self.buffs, self.penalties]:
			for mod_category in mod_type.values():
				if name in mod_category:
					if not mod_category[name]['disabled']:
						mod_category[name]['disabled'] = True
						self.update_value()
						return True
					return False
		return False
	
	def enable_mod(self, name):
		'''
			Enables a modifier if disabled. Returns whether the modifier was changed
			(True would mean that the buff has changed and so the gui needs updating...)
		'''
		for mod_type in [self.buffs, self.penalties]:
			for mod_category in mod_type.values():
				if name in mod_category:
					if mod_category[name]['disabled']:
						mod_category[name]['disabled'] = False
						self.update_value()
						return True
					return False
		return False

		
	
	def remove_mod(self, name):
		'''
			Attemps to remove a modifer as defined by it's name. Returns True if an element was removed
			(True would mean that the buff has changed and so the gui needs updating...)
		'''
		for mod_type in [self.buffs, self.penalties]:
			for mod_category in mod_type.values():
				try:
					del mod_category[name]
					self.update_value()
					return True
				except:
					pass
			return False
