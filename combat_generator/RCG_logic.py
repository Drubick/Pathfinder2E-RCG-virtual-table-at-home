from database import *
import random

class Generator:
	def __init__(self, path = "bestiary.db"):
		self._path = path
		self._database = Database(path)
		self._monster_list = []
		#temporal
		self._party_size = None
		self._encounter_threat  = None
		self._enemies_number = None
		self._threat_xp_difference = 40
		self._xp_budget = 0
		self._monster_xp_budget = 0
		self._cursor = None
		self._party_level = None
		self._query = None


	def get_xp_budget(self):
		xp_per_character = 0
		if self._encounter_threat == "Trivial":
			xp_per_character = 10
		elif self._encounter_threat == "Low":
			xp_per_character = 15
		elif self._encounter_threat == "Moderate":
			xp_per_character = 20
		elif self._encounter_threat == "Severe":
			xp_per_character = 30
		elif self._encounter_threat == "Extreme":
			xp_per_character = 40

		self._xp_budget = xp_per_character * self._party_size

	def determine_monster_max_level(self, xp):
		xp = self._xp_budget - xp
		if xp < 10:
			return -4
		elif xp >= 10 and xp < 15:
			return -3
		elif xp >= 15 and xp < 20:
			return -2
		elif xp >= 20 and xp < 40:
			return 0
		elif xp >= 40 and xp < 60:
			return 1
		elif xp >= 60 and xp < 80:
			return 2
		elif xp >= 80 and xp < 120:
			return 3
		elif xp >= 120 and xp <= 160:
			return 4
		else:
			return 4

	def determine_monster_xp(self, monster_level):
		monster_level_diff = monster_level - self._party_level
		lvl_to_xp = {-4:10, -3:15, -2:20, -1:30, 0:40, 1:60, 2:80, 3:120, 4:160}
		self._monster_xp_budget = lvl_to_xp[monster_level_diff]

	def get_monster_level(self, total_xp):
		lowest_level = self._party_level - 4
		highest_level = self._party_level + self.determine_monster_max_level(total_xp)
		if lowest_level < -1:
			lowest_level = -1
		if highest_level < -1:
			highest_level = -1 
		if self._encounter_threat == "Trivial":
			monster_level = random.randint(lowest_level, highest_level)
		elif self._encounter_threat == "Low":
			if highest_level> 21:
				highest_level = 21
			monster_level = random.randint(lowest_level, highest_level)
		elif self._encounter_threat == "Moderate":
			if highest_level> 21:
				highest_level = 21
			monster_level = random.randint(lowest_level, highest_level)
		elif self._encounter_threat == "Severe":
			if highest_level> 21:
				highest_level = 21
			monster_level = random.randint(lowest_level, highest_level)
		elif self._encounter_threat == "Extreme":
			if highest_level> 21:
				highest_level = 21
			monster_level = random.randint(lowest_level, highest_level)
		self.determine_monster_xp(monster_level)
		return monster_level

	def choose_monsters(self, total_xp):
		query =		Query("monsters")
		maximum_level = self._xp_budget
		monster_level = self.get_monster_level(total_xp)

		query.add_filter([MON.level, monster_level])
		query.limit = 1
		self._monster_list += self._database.search(query.compose_query())
		return self._monster_xp_budget

	def populate_encounter(self):
		total_xp = 0
		while  total_xp < self._xp_budget - 10:
			total_xp += self.choose_monsters(total_xp)
	
	def generate(self, party_size, party_level, encounter_threath):
		self._party_size = party_size
		self._party_level = party_level
		self._encounter_threat = encounter_threath
		self.get_xp_budget()
		self.populate_encounter()

if __name__ == "__main__":

	generator = Generator()
	generator.generate(4, 1, "Extreme")


	for monster in generator._monster_list:
		print(monster['name'])


#print(generator._monster_list)
#print(generator._monster_list)
#print(generator._database.search("monster_name", "level", 3))
