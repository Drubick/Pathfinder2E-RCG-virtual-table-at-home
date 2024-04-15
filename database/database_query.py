from enum import Enum

# IMPORT THIS CLASS USING import query.
# This makes it so that the SQL_OPERATOS
# and MON macros are imported

#Add here valid sql operators
class SQL_OP(Enum):
	AND =	'AND'
	OR =	'OR'
	LIKE =	'LIKE'
	IN =	'IN'


# Add here common value monster json paths.
# Levels are represented with .
#
# {
# 	'test': {
# 		'patata': 'frita'
# }
#  To get to the value frita == test.patata

class MON(Enum):
	level		= 'system.details.level.value'
	type		= 'system.details.creatureType'
	name		= 'name'
	ac			= 'system.attributes.ac.value'
	alingment	= 'system.details.alignment.value'
	traits		= 'system.traits.value'
	size		= 'system.traits.size.value'

class Query():

	@property
	def random(self):
		return self._random
	
	@random.setter
	def random(self, new_random_value: bool):
		if isinstance(new_random_value, bool):
			self._random = new_random_value
		else:
			raise(TypeError("Setting random with a non boolean!"))
		
	@property
	def limit(self):
		return self._limit
	
	@limit.setter
	def limit(self, new_limit_value: bool):
		if isinstance(new_limit_value, int) or not new_limit_value:
			self._limit = new_limit_value
		else:
			raise(TypeError("Setting limit with an int!"))
		
	def __str__(self) -> str:
		return self.compose_query()
		
	def __init__(self, table) -> None:
		self._table = table
		self.reset()

	def reset(self):
		self._random = True
		self._limit = None
		self._filter_search = []
		self._filter_fields = []
		self._filter_source = []
		
	def compose_query(self):
		source = f'(SELECT * FROM \'{self._table}\' ORDER BY RANDOM())' if self.random else f"'{self._table}'"
		limit = f' LIMIT {self.limit}' if self.limit else ''
		filter_fields = 'data' if not self._filter_fields else " ".join(self._filter_fields)
		filter_search = '' if not self._filter_search else ' WHERE ' + " ".join(self._filter_search)
		if self._filter_source:
			source_search = (' AND ' if self._filter_search else 'WHERE ') + f'source IN ({" ".join(self._filter_source)})' 
		else:
			source_search = ''
		
		return f'SELECT {filter_fields} FROM {source} {filter_search}{source_search}{limit}'

	def __get_query_start(self, previous_filters, previous_content_operator):
		# Error check the previous content operator and adds it to the query
		if len(previous_filters):
			if not previous_content_operator:
				raise(ValueError(f'No previous content operator supplied!\nCurrent content = self._filter_search'))
			# Convert to string if macro, else convert to uppercase to see if it's a macro
			if isinstance(previous_content_operator, Enum):
				previous_content_operator = previous_content_operator.value
			else:
				previous_content_operator = previous_content_operator.upper()
			if previous_content_operator not in SQL_OP._member_map_:
				raise(ValueError('Previous operator not in valid operators lists'))
			#If it's an enum gets it's actual value
			query_start = previous_content_operator + ' '
		else:
			query_start = ''
		return query_start

	def __add_filter_operator(self, arg, index):
		#Error check
		if not isinstance(arg, str):
			raise(ValueError(f'Invalid argument at index {index}: {arg};\nExpected an operator str!'))
		#Convert to upper to check if valid operator
		arg = arg.upper()
		if arg not in SQL_OP._member_map_:
			raise(ValueError(f'Invalid argument at index {index}: {arg};\nInvalid operator!'))
		
		return arg
	
	def __add_filter_statement(self, arg, index):

		if not isinstance(arg, list) and not isinstance(arg, tuple):
			raise(ValueError(f'Invalid argument at index {index}: {arg};\nExpected a statement tuple / list!'))
		#Convert macros to strings and add ' to value if it's a string (with content in it)
		arg = [element.value if isinstance(element, Enum) else f"'{element}'"
			if (isinstance(element, str) and index + 1 == len(arg) and len(element))
				else str(element) for index, element in enumerate(arg)]
		if len(arg) == 3:
			return f"json_extract(data, '$.{arg[0]}') {arg[1]} {arg[2]}"
		elif len(arg) == 2:
			return f"json_extract(data, '$.{arg[0]}') = {arg[1]}"
		else:
			raise(ValueError(f'Invalid argument at index {index}: {arg};\nNot enough tuple / list elements!'))

	def add_filter(self, *query_args, previous_content_operator = None):
		#Usage: Add filters by calling the add_filter function.
		#
		# For each function call:
		# You may add as many statments as you'd like per call. However, an operator must be given in between statements.
		# (Operator validity and grammar is checked (each statement has an operator in between, operators are valid...))
		# As for the statements, you have to provie a list / tuple with len of either 2 or 3 elements.
		# * 2 elements: Path | value; comparison operator is assumed to be '='
		# * 3 elements: Path | comparison operator | value

		# If the last element is a string, it's automatically enclosed in '' (if it has any lenght).
		# Note that this allows a little trickery:
		#	(path, 'SQL EXPRESION', '') <- The third element will left blank, so you can inyect a custom SQL statement.
		# Yes, I designed my own SQL inyection... :)

		# The resulting query part is enclosed in brackets and stored in a list (so we can remove individual pieces if we want later)

		# In between function calls
		# If a filter has been added already, a previous content operator is required (needs to be specified. previous content operator)
		# This allows for total flexibility in queries, since you can mix and match operators and sub statements

		#Adds and error checks the previous content operator
		query_start = self.__get_query_start(self._filter_search, previous_content_operator)		
		query_elements = []
		le_operator = True
		le_statement = False

		#le_ = last_element. Used to track what was last inserted
		for index, arg in enumerate(query_args):

			#Last inserted element was a statement (so the current element should be an operator)
			if le_statement:
				query_elements.append(self.__add_filter_operator(arg, index))
				le_operator, le_statement = le_statement, le_operator
			elif le_operator:
				#Store the operator and swap operator flags
				query_elements.append(self.__add_filter_statement(arg, index))
				le_operator, le_statement = le_statement, le_operator
		if le_operator: # Checks if there's a dangling operator
			raise(ValueError('Last query element is a dangling operator!'))
		final_query = f'{query_start}({" ".join(query_elements)})'
		self._filter_search.append(final_query)

	def add_source_filter(self, sources_to_filter):
		if isinstance(sources_to_filter, str):
			self._filter_source.append(f"'{sources_to_filter}'")
		elif isinstance(sources_to_filter, list):
			self._filter_source += [f"'{source}'" for source in sources_to_filter]
		else:
			raise(TypeError('Invalid source argument!'))


if __name__ == "__main__":
	query = Query('monsters')
	query.add_filter((MON.level, 15))
	query.add_source_filter('pathfinder-bestiary')
	# query.add_filter((MON.AC, '<=', 14), 'AND', (MON.Type, 'Dragon'), previous_content_operator='OR')

	print(query.compose_query())