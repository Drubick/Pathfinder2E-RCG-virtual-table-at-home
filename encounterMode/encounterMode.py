from infoFrame.infoFrame		import *
from creature.creature			import Creature
from creature.database_creature	import DatabaseCreature
from creature.player			import Player
from database.bestiary_database	import Database
from database.database_query	import *

class EncounterMode():
	def __init__(self, root, database:Database) -> None:
		self._database = database
		self._frame =		ttk.Frame(root)
		self._creatures =		[]
		self._creature_names =	[]
		self._infoFrame =	InfoFrame(self._database, self._frame)

		self._creatures_frame = ttk.Frame(self._frame, borderwidth=10)
		
		# Configure frame so the widgets expand when the parent frame is resized
		self._frame.grid_columnconfigure(0, weight=7)
		self._frame.grid_columnconfigure(1, weight=3)

		self._frame.grid_rowconfigure(0,	weight=1)
		self._frame.grid_rowconfigure(1,	weight=8)
		self._frame.grid_rowconfigure(2,	weight=1)
		
		# Configure creatures so that they expand when the parent frame is resized
		self._creatures_frame.grid_columnconfigure(0, weight=1)

		#Render the different widgets
		self._creatures_frame.grid(row=1, column=0, sticky= 'NSEW')
		self._infoFrame._frame.grid(row=0, column=1, rowspan=3, sticky='NSEW')

	def add_player(self, raw_data):
		if raw_data:
			if raw_data['name'] in self._creature_names:
				print('Player already present...')
				return
			self._creature_names.append(raw_data['name'])
			player = Player(self, self._creatures_frame, self._infoFrame, raw_data)
			if player:
				self._creatures.append(player)
			
			#Update the view
			self._creatures.append(player)
			self._creatures[-1]._frame.grid()
			self._creatures[-1]._frame.grid_configure(pady = 10)
			self._creatures[-1].index = len(self._creatures) - 1

	def add_database_monster(self, database_name, rename = None):
		query = Query('monsters')
		query.add_filter((MON.name, database_name))

		monster_raw = self._database.search(query.compose_query())
		if monster_raw:
			monster = DatabaseCreature(self, self._creatures_frame, self._infoFrame, monster_raw[0])
			self._creatures.append(monster)

			# Handle name update
			if rename:
				self._creatures[-1].change_name(rename)
			else:
				# If duplicated, name them differently (#2, #3...)
				self._creature_names.append(monster_raw[0]['name'])
				count = len([name for name in self._creature_names if name == monster_raw[0]['name']])
				if count > 1:
					self._creatures[-1].change_name(monster_raw[0]['name'] + f' #{count}')
				
			self._creatures[-1]._frame.grid()
			self._creatures[-1]._frame.grid_configure(pady = 10)
			self._creatures[-1].index = len(self._creatures) - 1
		else:
			print('Monster not found:', database_name)
	
	def _sort_by_initiative(self):
		creatures = sorted(self._creatures, key=lambda d: d.initiative)
		for creature in self._creatures:
			creature._frame.pack_forget()
		self._creatures = creatures
		for index, creature in enumerate(self._creatures):
			self._creatures[-1]._frame.grid(columnspan = 7)
			creature.index = index
	
	def _move_up(self, index):
		if index == 0 or index >= len(self._creatures):
			return
		#Unpack the required elements
		for i in range(index - 1, len(self._creatures)):
			self._creatures[i]._frame.pack_forget()
		
		#Swap the elements
		self._creatures[index], self._creatures[index - 1] = self._creatures[index - 1], self._creatures[index]
		self._creatures[index].index, self._creatures[index - 1].index = index, index - 1
		
		#Update the view
		for i in range(index - 1, len(self._creatures)):
			self._creatures[i]._frame.pack(fill=X, side='top', pady='10')
	
	def _move_down(self, index):
		if index == len(self._creatures) - 1 or index < 0:
			return
		#Unpack the required elements
		for i in range(index, len(self._creatures)):
			self._creatures[i]._frame.pack_forget()

		#Swap the elements
		self._creatures[index], self._creatures[index + 1] = self._creatures[index + 1], self._creatures[index]
		self._creatures[index].index, self._creatures[index + 1].index = index, index + 1
		
		#Update the view
		for i in range(index, len(self._creatures)):
			self._creatures[i]._frame.pack(fill=X, side='top', pady='10')


	def remove_creature(self, index = None, name = None):
		if (index) == (name):
			return
		if index != None:
			if index < 0 or index >= len(self._creatures):
				return
		else:
			for index, creature in enumerate(self._creatures):
				if creature.name == name:
					break
			else:
				return

		self._creatures[index]._frame.pack_forget()
		del self._creatures[index]
		for i in range(index, len(self._creatures)):
			self._creatures[i].index = i