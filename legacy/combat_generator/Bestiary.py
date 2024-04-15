from pprint import pprint
import sqlite3


class Bestiary:
	def __init__ (self, path):
		self._cursore = None
		self.connect_to_database(path)
		self._table_name = "Monsters"

	def __del_ (self):
		if self._conn:
			self._conn.close()
	
#methods	
	def connect_to_database(self, database_name):
		db_conn = sqlite3.connect(database_name)
		cursor = db_conn.cursor()
		self._cursor = cursor

	def select_table(self, table):
		self._table_name = table

	def search(self, info_to_fetch, search_criteria = None, search_criteria_value = None):
		if search_criteria and search_criteria_value:
			self._cursor.execute(
				f"SELECT level, {info_to_fetch} FROM {self._table_name} WHERE {search_criteria} = {search_criteria_value} ORDER BY RANDOM()")
		else:
			self._cursor.execute(f"SELECT {info_to_fetch} FROM {self._table_name} ORDER BY RANDOM()")
		return self._cursor.fetchone()

	def fetch_info_sorted(self, info_to_fetch, sort_criteria, search_criteria = None, search_criteria_value = None,):
		if search_criteria and search_criteria_value:
			self._cursor.execute( f"SELECT {info_to_fetch} FROM {self._table_name} WHERE {search_criteria} = {search_criteria_value} ORDER BY {sort_criteria}")
		else:
			self._cursor.execute(f"SELECT {info_to_fetch} FROM {self._table_name} ORDER BY {sort_criteria}")

monster = Bestiary("Bestiario.db")
#monster.connect_to_database("Bestiario.db")
#monster.select_table("Monsters")
monster.search("monster_name", "senses", "")
#monster._cursor.execute("SELECT monster_name FROM Monsters")
#print(monster._cursor.fetchall())