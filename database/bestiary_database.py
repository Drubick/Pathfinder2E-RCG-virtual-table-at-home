import sqlite3
import	json
import	os
from	pprint import pprint
import	re
from	bs4 import BeautifulSoup
import	requests

class Database():
	def __init__(self, path = 'bestiary.db') -> None:
		self._connection = sqlite3.connect(path)
		self._cursor = self._connection.cursor()
		self.database_references = {
			#@Check[type:athletics|dc:20|name:Unlodge Weapon]
			#@Check[type:flat|dc:11]
			'conditions':						['Compendium.pf2e.conditionitems.Item.'],
			'effects':							['Compendium.pf2e.other-effects.Item.'],
			'actions':							['Compendium.pf2e.actionspf2e.Item.'],
			'spells':							['Compendium.pf2e.spells-srd.Item.'],
			'bestiary-abilities':				['PF2E.NPC.Abilities.Glossary.']
		}
		# exit(1)

	def extract_reference(self, source_text):
		references = []
		expand = True
		source_text = BeautifulSoup(source_text, 'html.parser').get_text('').strip('\n')

		#TODO: Add the option to extract the whole item instead of the description?
		for reference in re.finditer(r'@(?:Localize|UUID)\[(.*?)\](?:{(.*?)})?', source_text):
			match_elements = reference.groups()
			search_string = match_elements[0]

			for database_key, search_string_matches in self.database_references.items():
				for match_string in search_string_matches:
					if match_string in search_string:
						search_table = database_key
						break
				else:
					continue
				break
			else:
				expand = False
				# raise(Exception(f'Match {search_string} not found in database_references!'))

			name = search_string[search_string.rfind('.') + 1:]
			if expand:
				query = f"SELECT data FROM '{search_table}'  WHERE (json_extract(data, '$.name') = '{name}') LIMIT 1"
				match_content = self.search(query)

				if match_content:
					expanded_text = match_content[0]['system']['description']['value']
				else:
					raise(Exception(f'Match {search_string} not found in the database (table = {search_table})!'))
			else:
				expanded_text = None
				
			link_text = match_elements[1] if match_elements[1] else name
			parsed_reference = {
				'span': reference.span(),
				'expand_text': expanded_text,
				'link_text': link_text
			}
			references.append(parsed_reference)
		return self._format_references(source_text, references)
	
	def _format_references(self, source_text, references):
		text_chunks = []
	
		last_index = 0
		for reference in references:
			text_chunks.append({
				'text': source_text[last_index:reference['span'][0]],
				'expandable': False
			})
			text_chunks.append({
				'text':				reference['link_text'],
				'expandable':		reference['expand_text'],
				'expand_text':	reference['expand_text']
			})
			last_index = reference['span'][1]
		
		text_chunks.append({
			'text': source_text[last_index:] if text_chunks else source_text,
			'expandable': False
		})
		return text_chunks


	def get_table_element_names(self, table):
		"""
			Retuns a list with the names of the elements of the given table
		"""
		results = [name[0] for name in self._cursor.execute(f"SELECT json_extract(data, '$.name') FROM '{table}';").fetchall()]
		results.sort()
		return results
		
	def get_tables(self):
		"""
			Retuns a list of the tables currently contained in the database
		"""

		return [table[0] for table in self._cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()]

	def get_sources(self, table):
		"""
			Returns a dictionary of the sources in a given dictionary:
			{
				source: amount of entries
			}
		"""
		sources = set()
		results = self._cursor.execute(f"SELECT source FROM '{table}';").fetchall()
		sources = {}
		for result in results:
			result = result[0]
			if result not in sources:
				sources[result] = 0
			else:
				sources[result] += 1
		return  sources
	
	def delete_table(self, table):
		if table not in self.get_tables():
			raise(Exception('Table not in database'))
		self._cursor.execute(f'DROP TABLE \'{table}\'')
		self._connection.commit()


	def load_jsons(self, folder_path, table, verbose = False):
		if table not in self.get_tables():
			if verbose:
				print(f'Creating table {table}')
			self._cursor.execute(f'CREATE TABLE \'{table}\' (id INTEGER PRIMARY KEY, data JSON, source TEXT);')

		source = os.path.split(folder_path)[1]
		current_sources = self.get_sources(table)

		if os.path.basename(folder_path) in current_sources:
			if verbose:
				print('Source already loaded!')
			return

		valid_json_paths = [file_path for file_path in os.listdir(folder_path) if file_path.endswith('.json')]
		
		#Get max_id
		res = self._cursor.execute(f"SELECT id FROM '{table}' ORDER BY id DESC LIMIT 1").fetchone()
		if res:
			start_index = res[0] + 1
		else:
			start_index = 0

		elements_to_insert = []
		for index, element, in enumerate(valid_json_paths):
			with open(os.path.join(folder_path, element), 'r') as file:
				json_data = json.load(file)
			elements_to_insert.append((start_index + index, json.dumps(json_data), source))

		query = f'INSERT INTO \'{table}\' VALUES (?,?,?);'
		self._cursor.executemany(query, elements_to_insert)
		self._connection.commit()
		if verbose:
			print('Loaded ' + folder_path)

	def search(self, query):
		#print(f'Query = {query}\n\n')
		# result = cursor.execute("SELECT json_extract(data, '$.email') AS email FROM users WHERE email = 'alice@example.com';")
	
		results = self._cursor.execute(query)
		parsed_results = []

		#Organize and return the results
		for result in results.fetchall():
			try:
				result = json.loads(result[0])
			except:
				result = result[0]
				# result = [result[0]]
			parsed_results.append(result)
			# if names[0] == 'monster_raw':
			# 	parsed_results.append({'monster_raw': result})
			# else:
			# 	parsed_results.append({names[i] : value for i, value in enumerate(result)})
		return parsed_results
		# return [Monster(monster_raw) for monster_raw in monsters_raw]

	def __del__(self):
		self._connection.close()

	def load_bestiary_effects(self, verbose = False):
		table = 'bestiary-abilities'
		if table not in self.get_tables():
			if verbose:
				print(f'Creating table {table}')
			self._cursor.execute(f'CREATE TABLE \'{table}\' (id INTEGER PRIMARY KEY, data JSON, source TEXT);')

		beastiary_abilities = {
			"All-Around Vision": "This monster can see in all directions simultaneously, and therefore can't be flanked.",
			"Aquatic Ambush": "Requirements The monster is hiding in water and a creature that hasn’t detected it is within the listed number of feet. Effect The monster moves up to its swim Speed + 10 feet toward the triggering creature, traveling on water and on land. Once the creature is in reach, the monster makes a Strike against it. The creature is flat-footed against this Strike.",
			"Attack Of Opportunity": "Trigger A creature within the monster's reach uses a manipulate action or a move action, makes a ranged attack, or leaves a square during a move action it's using. Effect The monster attempts a melee Strike against the triggering creature. If the attack is a critical hit and the trigger was a manipulate action, the monster disrupts that action. This Strike doesn't count toward the monster's multiple attack penalty, and its multiple attack penalty doesn't apply to this Strike.",
			"At-Will Spells": "The monster can cast its at-will spells any number of times without using up spell slots.",
			"Aura": "A monster's aura automatically affects everything within a specified emanation around that monster. The monster doesn't need to spend actions on the aura; rather, the aura's effects are applied at specific times, such as when a creature ends its turn in the aura or when creatures enter the aura.\n\nIf an aura does nothing but deal damage, its entry lists only the radius, damage, and saving throw. Such auras deal this damage to a creature when the creature enters the aura and when a creature starts its turn in the aura. A creature can take damage from the aura only once per round.\n\nThe GM might determine that a monster's aura doesn't affect its own allies. For example, a creature might be immune to a monster's frightful presence if they have been around each other for a long time.",
			"Buck": "Most monsters that serve as mounts can attempt to buck off unwanted or annoying riders, but most mounts will not use this reaction against a trusted creature unless the mounts are spooked or mistreated. Trigger A creature Mounts or uses the Command an Animal action while riding the monster. Effect The triggering creature must succeed at a Reflex saving throw against the listed DC or fall off the creature and land @UUID[Compendium.pf2e.conditionitems.Item.Prone]{Prone 1}. If the save is a critical failure, the triggering creature also takes 1d6 bludgeoning damage in addition to the normal damage for the fall.",
			"Catch Rock": "Requirements The monster must have a free hand but can Release anything it's holding as part of this reaction. Trigger The monster is targeted with a thrown rock Strike or a rock would fall on the monster. Effect The monster gains a +4 circumstance bonus to its AC against the triggering attack or to any defense against the falling rock. If the attack misses or the monster successfully defends against the falling rock, the monster catches the rock, takes no damage, and is now holding the rock.",
			"Change Shape": "(concentrate, [magical tradition], polymorph, transmutation) The monster changes its shape indefinitely. It can use this action again to return to its natural shape or adopt a new shape. Unless otherwise noted, a monster cannot use Change Shape to appear as a specific individual. Using Change Shape counts as creating a disguise for the Impersonate use of Deception. The monster's transformation automatically defeats Perception DCs to determine whether the creature is a member of the ancestry or creature type into which it transformed, and it gains a +4 status bonus to its Deception DC to prevent others from seeing through its disguise. Change Shape abilities specify what shapes the monster can adopt. The monster doesn't gain any special abilities of the new shape, only its physical form. For example, in each shape, it replaces its normal Speeds and Strikes, and might potentially change its senses or size. Any changes are listed in its stat block.",
			"Constant Spells": "A constant spell affects the monster without the monster needing to cast it, and its duration is unlimited. If a constant spell gets counteracted, the monster can reactivate it by spending the normal spellcasting actions the spell requires.",
			"Constrict": "The monster deals the listed amount of damage to any number of creatures @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} or @UUID[Compendium.pf2e.conditionitems.Item.Restrained]{Restrained 1} by it. Each of those creatures can attempt a basic Fortitude save with the listed DC.",
			"Coven": "(divination, mental, occult) This monster can form a coven with two or more other creatures who also have the coven ability. This involves performing an 8-hour ceremony with all prospective coven members. After the coven is formed, each of its members gains elite adjustments, adjusting their levels accordingly. Coven members can sense other members’ locations and conditions by spending a single action, which has the concentrate trait, and can sense what another coven member is sensing as a two-action activity, which has the concentrate trait as well.\n\nCovens also grant spells and rituals to their members, but these can be cast only in cooperation between three coven members who are all within 30 feet of one another. A coven member can contribute to a coven spell with a single-action spellcasting activity that has a single verbal component. If two coven members have contributed these actions within the last round, a third member can cast a coven spell on her turn by spending the normal spellcasting actions. A coven can cast its coven spells an unlimited number of times but can cast only one coven spell each round. All covens grant the 8th-level baleful polymorph spell and all the following spells, which the coven can cast at any level up to 5th: augury, charm, clairaudience, clairvoyance, dream message, illusory disguise, illusory scene, prying eye, and talking corpse. Individual creatures with the coven ability also grant additional spells to any coven they join. A coven can also cast the control weather ritual, with a DC of 23 instead of the standard DC.\n\nIf a coven member leaving the coven or the death of a coven member brings the coven below three members, the remaining members keep their elite adjustments for 24 hours, but without enough members to contribute the necessary actions, they can’t cast coven spells.",
			"Darkvision": "A monster with darkvision can see perfectly well in areas of darkness and dim light, though such vision is in black and white only. Some forms of magical darkness, such as a 4th-level darkness spell, block normal darkvision. A monster with greater darkvision, however, can see through even these forms of magical darkness.",
			"Disease": "When a creature is exposed to a monster’s disease, it attempts a Fortitude save or succumbs to the disease. The level of a disease is the level of the monster inflicting the disease. The disease follows the rules for afflictions.",
			"Engulf": "The monster Strides up to double its Speed and can move through the spaces of any creatures in its path. Any creature of the monster’s size or smaller whose space the monster moves through can attempt a Reflex save with the listed DC to avoid being engulfed. A creature unable to act automatically critically fails this save. If a creature succeeds at its save, it can choose to be either pushed aside (out of the monster’s path) or pushed in front of the monster to the end of the monster’s movement. The monster can attempt to Engulf the same creature only once in a single use of Engulf. The monster can contain as many creatures as can fit in its space.\n\nA creature that fails its save is pulled into the monster’s body. It is @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1}, is @UUID[Compendium.pf2e.conditionitems.Item.Slowed]{Slowed 1}, and has to hold its breath or start suffocating. The creature takes the listed amount of damage when first engulfed and at the end of each of its turns while it’s engulfed. An engulfed creature can get free by Escaping against the listed escape DC. An engulfed creature can attack the monster engulfing it, but only with unarmed attacks or with weapons of light Bulk or less. The engulfing creature is flat-footed against the attack. If the monster takes piercing or slashing damage equaling or exceeding the listed Rupture value from a single attack or spell, the engulfed creature cuts itself free. A creature that gets free by either method can immediately breathe and exits the swallowing monster’s space.\n\nIf the monster dies, all creatures it has engulfed are automatically released as the monster’s form loses cohesion.",
			"Fast Healing": "A monster with this ability regains the given number of Hit Points each round at the beginning of its turn.",
			"Ferocity": "Trigger The monster is reduced to 0 HP. Effect The monster avoids being knocked out and remains at 1 HP, but its @UUID[Compendium.pf2e.conditionitems.Item.Wounded]{Wounded 1} value increases by 1. When it is @UUID[Compendium.pf2e.conditionitems.Item.Wounded]{Wounded 3}, it can no longer use this ability.",
			"Form Up": "The troop chooses one of the squares it currently occupies and redistributes its squares to any configuration in which all squares are contiguous and within 15 feet of the chosen square. The troop can't share its space with other creatures.",
			"Frightful Presence": "(aura, emotion, fear, mental) A creature that first enters the area must attempt a Will save. Regardless of the result of the saving throw, the creature is temporarily immune to this monster’s Frightful Presence for 1 minute.\n\nCritical Success The creature is unaffected by the presence.\n\nSuccess The creature is @UUID[Compendium.pf2e.conditionitems.Item.Frightened]{Frightened 1}.\nFailure The creature is @UUID[Compendium.pf2e.conditionitems.Item.Frightened]{Frightened 2}.\nCritical Failure The creature is @UUID[Compendium.pf2e.conditionitems.Item.Frightened]{Frightened 4}.",
			"Grab": "Requirements The monster's last action was a successful Strike that lists Grab in its damage entry, or the monster has a creature @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} or @UUID[Compendium.pf2e.conditionitems.Item.Restrained]{Restrained 1}; Effect If used after a Strike, the monster attempts to Grapple the creature using the body part it attacked with. This attempt neither applies nor counts toward the creature's multiple attack penalty.\n\nThe monster can instead use Grab and choose one creature it's grabbing or restraining with an appendage that has Grab to automatically extend that condition to the end of the monster's next turn.",
			"Greater Constrict": "The monster deals the listed amount of damage to any number of creatures @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} or @UUID[Compendium.pf2e.conditionitems.Item.Restrained]{Restrained 1} by it. Each of those creatures can attempt a basic Fortitude save with the listed DC. A creature that fails this save falls @UUID[Compendium.pf2e.conditionitems.Item.Unconscious]{Unconscious 1}, and a creature that succeeds is then temporarily immune to falling @UUID[Compendium.pf2e.conditionitems.Item.Unconscious]{Unconscious 1} from Greater Constrict for 1 minute.",
			"Improved Grab": "The monster can use Grab as a free action triggered by a hit with its initial attack. A monster with Improved Grab still needs to spend an action to extend the duration for creatures it already has @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1}.",
			"Improved Knockdown": "The monster can use Knockdown as a free action triggered by a hit with its initial attack.",
			"Improved Push": "The monster can use Push as a free action triggered by a hit with its initial attack.",
			"Knockdown": "Requirements The monster's last action was a successful Strike that lists Knockdown in its damage entry; Effect The monster attempts to Trip the creature. This attempt neither applies nor counts toward the monster's multiple attack penalty.",
			"Lifesense": "Lifesense allows a monster to sense the vital essence of living and undead creatures within the listed range. The sense can distinguish between the positive energy animating living creatures and the negative energy animating undead creatures, much as sight distinguishes colors.",
			"Light Blindness": "When first exposed to bright light, the monster is @UUID[Compendium.pf2e.conditionitems.Item.Blinded]{Blinded 1} until the end of its next turn. After this exposure, light doesn’t blind the monster again until after it spends 1 hour in darkness. However, as long as the monster is in an area of bright light, it’s @UUID[Compendium.pf2e.conditionitems.Item.Dazzled]{Dazzled 1}.",
			"Low-Light Vision": "The monster can see in dim light as though it were bright light, so it ignores the @UUID[Compendium.pf2e.conditionitems.Item.Concealed]{Concealed 1} condition due to dim light.",
			"Negative Healing": " A creature with negative healing draws health from negative energy rather than positive energy. It is damaged by positive damage and is not healed by positive healing effects. It does not take negative damage, and it is healed by negative effects that heal undead.",
			"Poison": "When a creature is exposed to a monster’s poison, it attempts a Fortitude save to avoid becoming poisoned. The level of a poison is the level of the monster inflicting the poison. The poison follows the rules for afflictions.",
			"Push": "Requirements The monster's last action was a successful Strike that lists Push in its damage entry; Effect The monster attempts to Shove the creature. This attempt neither applies nor counts toward the monster's multiple attack penalty. If Push lists a distance, change the distance the creature is pushed on a success to that distance.",
			"Reactive Strike": "Trigger A creature within the monster's reach uses a manipulate action or a move action, makes a ranged attack, or leaves a square during a move action it's using; Effect The monster attempts a melee Strike against the triggering creature. If the attack is a critical hit and the trigger was a manipulate action, the monster disrupts that action. This Strike doesn't count toward the monster's multiple attack penalty, and its multiple attack penalty doesn't apply to this Strike.",
			"Regeneration": "This monster regains the listed number of Hit Points each round at the beginning of its turn. Its @UUID[Compendium.pf2e.conditionitems.Item.Dying]{Dying 1} condition never increases beyond @UUID[Compendium.pf2e.conditionitems.Item.Dying]{Dying 3} as long as its regeneration is active. However, if it takes damage of a type listed in the regeneration entry, its regeneration deactivates until the end of its next turn. Deactivate the regeneration before applying any damage of a listed type, since that damage might kill the monster by bringing it to @UUID[Compendium.pf2e.conditionitems.Item.Dying]{Dying 4}.",
			"Rend": "A Rend entry lists a Strike the monster has. Requirements The monster hit the same enemy with two consecutive Strikes of the listed type in the same round. Effect The monster automatically deals that Strike’s damage again to the enemy.",
			"Retributive Strike": "Trigger An enemy damages the monster’s ally, and both are within 15 feet of the monster. Effect The ally gains resistance to all damage against the triggering damage equal to 2 + the monster’s level. If the foe is within reach, the monster makes a melee Strike against it.",
			"Scent": "Scent involves sensing creatures or objects by smell, and is usually a vague sense. The range is listed in the ability, and it functions only if the creature or object being detected emits an aroma (for instance, incorporeal creatures usually do not exude an aroma).\n\nIf a creature emits a heavy aroma or is upwind, the GM can double or even triple the range of scent abilities used to detect that creature, and the GM can reduce the range if a creature is downwind.",
			"Shield Block": "Trigger The monster has its shield raised and takes damage from a physical attack. Effect The monster snaps its shield into place to deflect a blow. The shield prevents the monster from taking an amount of damage up to the shield’s Hardness. The monster and the shield each take any remaining damage, possibly breaking or destroying the shield.",
			"Sneak Attack": "When the monster Strikes a creature that has the flat-footed condition with an agile or finesse melee weapon, an agile or finesse unarmed attack, or a ranged weapon attack, it also deals the listed precision damage. For a ranged attack with a thrown weapon, that weapon must also be an agile or finesse weapon.",
			"Swallow Whole": "The monster attempts to swallow a creature of the listed size or smaller that it has @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} in its jaws or mouth. If a swallowed creature is of the maximum size listed, the monster can’t use Swallow Whole again. If the creature is smaller than the maximum, the monster can usually swallow more creatures; the GM determines the maximum. The monster attempts an Athletics check opposed by the @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} creature’s Reflex DC. If it succeeds, it swallows the creature. The monster’s mouth or jaws no longer grab a creature it has swallowed, so the monster is free to use them to Strike or Grab once again. The monster can’t attack creatures it has swallowed.\n\nA swallowed creature is @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1}, is @UUID[Compendium.pf2e.conditionitems.Item.Slowed]{Slowed 1}, and has to hold its breath or start suffocating. The swallowed creature takes the listed amount of damage when first swallowed and at the end of each of its turns while it’s swallowed. If the victim Escapes this ability’s @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} condition, it exits through the monster’s mouth. This frees any other creature @UUID[Compendium.pf2e.conditionitems.Item.Grabbed]{Grabbed 1} in the monster’s mouth or jaws. A swallowed creature can attack the monster that has swallowed it, but only with unarmed attacks or with weapons of light Bulk or less. The engulfing creature is flat-footed against the attack. If the monster takes piercing or slashing damage equaling or exceeding the listed Rupture value from a single attack or spell, the engulfed creature cuts itself free. A creature that gets free by either Escaping or cutting itself free can immediately breathe and exits the swallowing monster’s space.\n\nIf the monster dies, a swallowed creature can be freed by creatures adjacent to the corpse if they spend a combined total of 3 actions cutting the monster open with a weapon or unarmed attack that deals piercing or slashing damage.",
			"Swarm Mind": "This monster doesn’t have a single mind (typically because it’s a swarm of smaller creatures), and is immune to mental effects that target only a specific number of creatures. It is still subject to mental effects that affect all creatures in an area.",
			"Telepathy": "(aura, divination, magical) A monster with telepathy can communicate mentally with any creatures within the listed radius, as long as they share a language. This doesn’t give any special access to their thoughts, and communicates no more information than normal speech would.",
			"Throw Rock": "The monster picks up a rock within reach or retrieves a stowed rock and throws it, making a ranged Strike.",
			"Trample": "The monster Strides up to double its Speed and can move through the spaces of creatures of the listed size, Trampling each creature whose space it enters. The monster can attempt to Trample the same creature only once in a single use of Trample. The monster deals the damage of the listed Strike, but trampled creatures can attempt a basic Reflex save at the listed DC (no damage on a critical success, half damage on a success, double damage on a critical failure).",
			"Tremorsense": "Tremorsense allows a monster to feel the vibrations through a solid surface caused by movement. It is an imprecise sense with a limited range (listed in the ability). Tremorsense functions only if the monster is on the same surface as the subject, and only if the subject is moving along (or burrowing through) the surface.",
			"Troop Defenses": "Troops are composed of many individuals, and over the course of enough attacks and downed comrades, troops shrink in size. Most troops start with 16 squares (4 by 4), and their Hit Points have two listed thresholds, typically the first is at 2/3 their maximum Hit Points and the second is at 1/3 their maximum Hit Points. Once the troop drops below the first threshold, it loses 4 squares, leaving 12 squares remaining, and the first threshold becomes the troop's new maximum Hit Points. Once the troop falls below the second threshold, it loses another 4 squares, leaving 8 squares remaining, and the second threshold becomes the troop's new maximum Hit Points. In order to restore its size and maximum Hit Points, a troop needs to spend downtime to use long-term treatment on casualties or recruit new members to replace the fallen. At 0 Hit Points, the troop is reduced down to 4 squares, which is too few to sustain the troop, so it disperses entirely, with the few remaining members surrendering, @UUID[Compendium.pf2e.conditionitems.Item.Fleeing]{Fleeing 1}, or easily dispatched, depending on their nature.\n\nA damaging single-target effect, such as a Strike, can't force a troop to pass through more than one threshold at once. For instance, if a troop had 60 Hit Points, with thresholds at 40 and 20, a Strike for 50 damage would leave the troop at 21 Hit Points, just above the second threshold. A damaging area effect or multi-target effect can cross multiple thresholds at once and could potentially destroy the entire troop in one shot.\n\nNon-damaging effects with an area or that target all creatures in a certain proximity affect a troop normally if they affect the entire area occupied by the troop. If an effect has a smaller area or numbers of targets, it typically has no effect on the troop. However, if the effect can target at least four creatures or cover at least four squares in the troop, and if it would prevent its targets from acting, cause them to flee, or otherwise make them unable to function as part of the troop for a round or more, the troop loses a number of Hit Points equal to the amount required to bring it to the next threshold, removing 4 squares. If an effect would both deal damage and automatically cross a threshold due to incapacitating some of the creatures in the troop, apply the damage first. If the damage wasn't enough to cross a threshold on its own, then reduce the Hit Points to cross the threshold for the incapacitating effect.",
			"Wavesense": "This sense allows a monster to feel vibrations caused by movement through a liquid. It’s an imprecise sense with a limited range (listed in the ability). Wavesense functions only if monster and the subject are in the same body of liquid, and only if the subject is moving through the liquid."
		}

		elements_to_insert = []

		for index, data in enumerate(beastiary_abilities.items()):
			raw_data = {'name': data[0].replace(' ', ''), 'system': {'description':{'value': data[1]}}}
			elements_to_insert.append((index, json.dumps(raw_data), 'Archives of Nethys'))

		query = f'INSERT INTO \'{table}\' VALUES (?,?,?);'
		self._cursor.executemany(query, elements_to_insert)
		self._connection.commit()


def load_bestiaries(database, folder_path):
	valid_bestiaries_folders = [os.path.join(folder_path, file_path) for file_path in os.listdir(folder_path) if (not file_path.startswith('bestiary') and 'bestiary' in file_path)]

	for bestiary_folder in valid_bestiaries_folders:
		database.load_jsons(bestiary_folder, 'monsters')

def load_effects(database, folder_path):
	valid_effect_folders = [os.path.join(folder_path, file_path) for file_path in os.listdir(folder_path) if ('effect' in file_path)]

	for effect_folder in valid_effect_folders:
		database.load_jsons(effect_folder, 'effects')

if __name__ == "__main__":
	from database_query import *

	database = Database('bestiary.db')

	# Clears all the tables from the database
	reset_database =	True

	# Loads all of the default tables
	load_auto =			True

	if reset_database:
		for table in database.get_tables():
			database.delete_table(table)
			
	# Automatic loading of certain packs
	if load_auto:
		path = input('Please input path to import from:\n')
		tables_to_load = (
			'criticalhit',
			'criticalfumble',
			'conditions',
			'ancestryfeatures',
			'backgrounds',
			'classes',
			'classfeatures',
			'feats',
			'actions',
			'ancestries',
			'spell-effects',
			'spell-effects',
			'spells'
		)
		for table in  tables_to_load:
			database.load_jsons(os.path.join(path, table), table)
		load_bestiaries(database, path)
		database.load_bestiary_effects()
		load_effects(database, path)

		#Adding non bestiary labeled monsters to the database
		database.load_jsons(os.path.join(path, 'npc-gallery'), 'monsters', '')

	if not database.get_tables():
		print('No tables loaded on the database')
		exit(1)

	print('Current database tables:')
	for table in database.get_tables():
		print(f'  * {table}')
	
	# #Prints the folders from which a table was loaded, and the amount of elements per source
	# pprint(database.get_sources('effects'))

	#Sample query to draw a critical fumble card

	# query = Query('criticalfumble')
	# query.limit = 1
	# print(query.compose_query())
	# cards = database.search(query.compose_query())

	# for card in cards:
	# 	source_text = card['pages'][0]['text']['content']

	# # 	print('\n\nBefore expansion:\n', source_text)
	# 	references = database.extract_reference(source_text)
	# 	pass

	# monster = bestiary.search("SELECT data FROM monsters WHERE (json_extract(data, '$.system.details.level.value') = 0) LIMIT 1")
	# print(monster)