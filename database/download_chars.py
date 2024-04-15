import requests
import time
import sqlite3
import json
from pprint import pprint

# res = cur.execute("DELETE FROM character")

# cur.execute("CREATE TABLE character(class, level, raw, pb_id)")

# last_inserted_value = cur.execute("SELECT * FROM character ORDER BY pb_id DESC LIMIT 1").fetchall()
# print(last_inserted_value)
# res = cur.execute("SELECT * FROM character WHERE class = \"Barbarian\" AND level = 4")


# res = cur.execute("SELECT * FROM character")
# for character in res.fetchall():
# 	# res = cur.execute(f"SELECT * FROM character WHERE id = {i}")
# 	pass
# 	race = json.loads(character[2])['ancestry'].replace('\'', '')
# 	result = cur.execute(f"UPDATE character\n SET race = '{race}' WHERE pb_id = {character[3]}")
# 	con.commit()
# exit(1)


# print(len(res.fetchall()))

# 

# race = 'AND race = Goblin'



class CharDownloader():
	def __init__(self) -> None:
		self.db_connection = sqlite3.connect("npc_enemies.db")
		self.cursor = self.db_connection.cursor()

	def fetch_characters(self, level, ch_class = '', race = '', random = False, limit = None):
		

		#Search by class / race
		if race:
			race = f" AND race = '{race}'"
		if ch_class:
			ch_class = f" AND class = '{ch_class}'"
		#Search limiters
		limit =		f' LIMIT {limit}' if limit else ''
	
		#Randomize search if needed
		query = 'SELECT * FROM '
		query += '(SELECT * FROM character ORDER BY RANDOM())' if random else 'character'

		#Compose final query
		query += f' WHERE level = {level}{race}{ch_class}{limit}'
		search_results = self.cursor.execute(query)

		character_jsons = [json.loads(character[2]) for character in search_results]

		return character_jsons


		for index, char in enumerate(res.fetchall()):
			with open(f'characters/{char[0]}_{index}.json', 'w+') as file:
				json.dump(json.loads(char[2]), file, indent=4)
			print(char[0], char[4])
			if index == 10:
				break
			break

	
	def download_characters(self, nb_of_batches = None):
		res = self.cursor.execute("SELECT pb_id FROM character ORDER BY pb_id DESC LIMIT 1")
		start_index = res.fetchone()[0] + 1

		end_index = 300000 if not nb_of_batches else start_index + nb_of_batches * 20

		for i in range(start_index, end_index):
			req = requests.get(f'https://pathbuilder2e.com/json.php', headers={
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
			}, params= {
				'id': 154627 #i
			})
			if req.status_code != 200:
				print('Error whilst requesting!')
				print(req.content)
				break
			else:
				character = req.json()
				if character['success'] != True or not character['build']:
					continue
				character = character["build"]
				with open('Nathaniel.json', 'w+') as file:
					json.dump(character, file)
				print(f'{character["class"]}, lvl {character["level"]}')
				self.cursor.executemany("INSERT INTO character VALUES(?, ?, ?, ?, ?)", [(character["class"], character["level"], json.dumps(character), i, character['ancestry'].replace('\'', ''))])
				self.db_connection.commit()				
				if (i % 20 == 0):
					self.db_connection.commit()
					print(f'20 NPCS added, current id = {i};\nCurrent run fetched amount = {i - start_index + 1}\n')


char_handler = CharDownloader()
char_handler.download_characters(500)
exit(1)

characters = char_handler.fetch_characters(20, 'Barbarian', random=True)
print(characters[0])
exit()
for character in characters:
	print(character['name'])