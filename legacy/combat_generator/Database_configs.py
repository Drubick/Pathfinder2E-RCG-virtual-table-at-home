import os
import glob
import json
import sqlite3

class Database:
	def __init__(self):
		self._conn = None
		self._conn = None
		pass

	def __del__(self):
		if self._conn:
			self._conn.close()

#methods
	def create_database(self, database_name):
		self._conn = sqlite3.connect(database_name)
		self._cursor = self._conn.cursor()
		try:
			#hacer que puedas crear como quieras la tabla mediante input u otro metodo
			self._cursor.execute("""CREATE TABLE Monsters
					(
					monster_name string,
					charisma integer,
					constitution integer,
					dexterity integer,
					intelect integer,
					strenght integer,
					wisdom integer,
					ac integer,
					special_saves string,
					hp integer,
					perception integer,
					speed integer,
					other_speeds string,
					alignement string,
					creature_type string,
					level integer,
					description string,
					fortitude_save integer,
					reflex_save integer,
					will_save integer,
					languages string,
					rarity string,
					senses string,
					size string,
					traits string,
						
					abilities_and_spells JSON
					   )""")
		except Exception as e:
			pass
		self._conn.commit()

	def load_json_to_database(self, path):
		json_paths = []
		data = []
		if os.path.isdir(path):
			for root, dirs, files in os.walk(path):
				files = glob.glob(os.path.join(root, '*.json'))
				json_paths = [os.path.abspath(f) for f in files if f.endswith(".json")]
		elif os.path.isfile(path):
			json_paths = [path]

		for path in json_paths:
			with open(path, "r") as file:
				json_data = json.load(file)
			data.append(json_data)
		return data

	def populate_database(self):
		rows = []
		data = self.load_json_to_database("Dungeon-crawler/combat_generator/base_bestiary/pathfinder-bestiary")
		for json_data in data:
			rows.append((
				json_data['name'],
				json_data['system']['abilities']['cha']['mod'], #int
				json_data['system']['abilities']['con']['mod'], #int
				json_data['system']['abilities']['dex']['mod'], #int
				json_data['system']['abilities']['int']['mod'], #int
				json_data['system']['abilities']['str']['mod'], #int
				json_data['system']['abilities']['wis']['mod'], #i
				json_data['system']['attributes']['ac']['value'], #int
				json_data['system']['attributes']['allSaves']['value'], #str
				json_data['system']['attributes']['hp']['value'], #int
				json_data['system']['attributes']['perception']['value'],#int
				json_data['system']['attributes']['speed']['value'],#int
				str(json_data['system']['attributes']['speed']['otherSpeeds']),
				json_data['system']['details']['alignment']['value'],#char
				json_data['system']['details']['creatureType'],#char
				json_data['system']['details']['level']['value'],#int
				json_data['system']['details']['publicNotes'],#i
				json_data['system']['saves']['fortitude']['value'],#int
				json_data['system']['saves']['reflex']['value'],#int
				json_data['system']['saves']['will']['value'], #i
				str(json_data['system']['traits']['languages']['value']),
				json_data['system']['traits']['rarity'],
				json_data['system']['traits']['senses']['value'],
				json_data['system']['traits']['size']['value'],
				str(json_data['system']['traits']['value']),
				json.dumps(json_data['items'])
						))
		format = ",".join(["?" for i in range(len(rows[0]))])
		query = f'insert into Monsters values ({format})'
		self._cursor.executemany(query, rows)
		self._conn.commit()