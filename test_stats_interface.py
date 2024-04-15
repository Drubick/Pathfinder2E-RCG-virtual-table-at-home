if __name__ == "__main__":
	from tkinter import *
	from database.bestiary_database import Database
	from infoFrame.infoFrame import InfoFrame
	from creature.database_creature import *
	from creature.player import *
	from encounterMode.encounterMode import EncounterMode
	from bs4 import BeautifulSoup



	import requests

	database = Database()

	root = Tk()
	root.geometry('1000x800')

	encounter = EncounterMode(root, database)
	encounter._frame.pack(expand=True, fill='both')
	encounter.add_player({
	"name": "Nathaniel Underwood ",
	"class": "Summoner",
	"dualClass": None,
	"level": 4,
	"ancestry": "Human",
	"heritage": "Versatile Heritage",
	"background": "Noble (Genealogy)",
	"alignment": "N",
	"gender": "Not set",
	"age": "Not set",
	"deity": "Not set",
	"size": 2,
	"sizeName": "Medium",
	"keyability": "cha",
	"languages": [
		"Abyssal",
		"Common"
	],
	"rituals": [
		"Teleportation Circle",
		"Infernal Pact",
		"Owb Pact",
		"Animate Object"
	],
	"resistances": [],
	"attributes": {
		"ancestryhp": 8,
		"classhp": 10,
		"bonushp": 0,
		"bonushpPerLevel": 0,
		"speed": 25,
		"speedBonus": -10
	},
	"abilities": {
		"str": 12,
		"dex": 14,
		"con": 16,
		"int": 10,
		"wis": 10,
		"cha": 16,
		"breakdown": {
			"ancestryFree": [
				"Con",
				"Dex"
			],
			"ancestryBoosts": [],
			"ancestryFlaws": [],
			"backgroundBoosts": [
				"Cha",
				"Con"
			],
			"classBoosts": [
				"Cha"
			],
			"mapLevelledBoosts": {
				"1": [
					"Cha",
					"Str",
					"Con",
					"Dex"
				]
			}
		}
	},
	"proficiencies": {
		"classDC": 2,
		"perception": 4,
		"fortitude": 4,
		"reflex": 2,
		"will": 4,
		"heavy": 0,
		"medium": 2,
		"light": 2,
		"unarmored": 2,
		"advanced": 0,
		"martial": 0,
		"simple": 2,
		"unarmed": 2,
		"castingArcane": 0,
		"castingDivine": 2,
		"castingOccult": 0,
		"castingPrimal": 0,
		"acrobatics": 0,
		"arcana": 0,
		"athletics": 2,
		"crafting": 0,
		"deception": 2,
		"diplomacy": 0,
		"intimidation": 2,
		"medicine": 0,
		"nature": 0,
		"occultism": 4,
		"performance": 0,
		"religion": 2,
		"society": 2,
		"stealth": 0,
		"survival": 0,
		"thievery": 0
	},
	"mods": {},
	"feats": [
		[
			"Courtly Graces",
			None,
			"Awarded Feat",
			1
		],
		[
			"Advanced Weaponry",
			None,
			"Summoner Evolution Feat",
			1
		],
		[
			"Versatile Heritage",
			None,
			"Heritage",
			1
		],
		[
			"Shield Block",
			None,
			"General Feat",
			1
		],
		[
			"Natural Ambition",
			None,
			"Ancestry Feat",
			1
		],
		[
			"Meld Into Eidolon",
			None,
			"Class Feat",
			1
		],
		[
			"Expanded Senses",
			None,
			"Class Feat",
			2
		],
		[
			"Intimidating Glare",
			None,
			"Skill Feat",
			2
		],
		[
			"Sentinel Dedication",
			None,
			"Archetype Feat",
			2
		],
		[
			"Slippery Prey",
			None,
			"General Feat",
			3
		],
		[
			"Group Coercion",
			None,
			"Skill Feat",
			4
		],
		[
			"Ritualist Dedication",
			None,
			"Archetype Feat",
			4
		],
		[
			"Lifelink Surge",
			None,
			"Class Feat",
			4
		]
	],
	"specials": [
		"Demonic Strikes",
		"Share Senses",
		"Act Together",
		"Demon Eidolon",
		"Link Spells",
		"Manifest Eidolon",
		"Evolution Feat",
		"Unlimited Signature Spells",
		"Shared Vigilance",
		"Versatile Heritage"
	],
	"lores": [
		[
			"Genealogy",
			2
		]
	],
	"equipmentContainers": {
		"43200c38-967b-4ec7-ac67-7efb8c119ba7": {
			"containerName": "Backpack",
			"bagOfHolding": False,
			"backpack": True
		}
	},
	"equipment": [
		[
			"Waterskin",
			1,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Rope",
			1,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Flint and Steel",
			1,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Healing Potion (Lesser)",
			2,
			"Invested"
		],
		[
			"Bedroll",
			1,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Soap",
			1,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Healer's Tools",
			1,
			"Invested"
		],
		[
			"Rations",
			2,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Bolts",
			20,
			"Invested"
		],
		[
			"Torch",
			5,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Chalk",
			10,
			"43200c38-967b-4ec7-ac67-7efb8c119ba7",
			"Invested"
		],
		[
			"Backpack",
			1,
			"Invested"
		],
		[
			"Healing Potion (Minor)",
			2,
			"Invested"
		],
		[
			"Vial de small polimorf",
			1,
			"Invested"
		]
	],
	"specificProficiencies": {
		"trained": [],
		"expert": [],
		"master": [],
		"legendary": []
	},
	"weapons": [
		{
			"name": "Mace",
			"qty": 1,
			"prof": "simple",
			"die": "d6",
			"pot": 0,
			"str": "",
			"mat": None,
			"display": "Mace",
			"runes": [],
			"damageType": "B",
			"attack": 7,
			"damageBonus": 1,
			"extraDamage": []
		},
		{
			"name": "Throwing Knife",
			"qty": 1,
			"prof": "simple",
			"die": "d4",
			"pot": 0,
			"str": "",
			"mat": None,
			"display": "Throwing Knife",
			"runes": [],
			"damageType": "P",
			"attack": 8,
			"damageBonus": 1,
			"extraDamage": []
		},
		{
			"name": "Longspear",
			"qty": 1,
			"prof": "simple",
			"die": "d8",
			"pot": 0,
			"str": "",
			"mat": None,
			"display": "Longspear",
			"runes": [],
			"damageType": "P",
			"attack": 7,
			"damageBonus": 1,
			"extraDamage": []
		},
		{
			"name": "Crossbow",
			"qty": 1,
			"prof": "simple",
			"die": "d8",
			"pot": 0,
			"str": "",
			"mat": None,
			"display": "Crossbow",
			"runes": [],
			"damageType": "P",
			"attack": 8,
			"damageBonus": 0,
			"extraDamage": []
		}
	],
	"money": {
		"cp": 1,
		"sp": 5,
		"gp": 9,
		"pp": 0
	},
	"armor": [
		{
			"name": "Lattice Armor",
			"qty": 1,
			"prof": "medium",
			"pot": 0,
			"res": "",
			"mat": None,
			"display": "Lattice Armor",
			"worn": True,
			"runes": []
		},
		{
			"name": "Tower Shield",
			"qty": 1,
			"prof": "shield",
			"pot": 0,
			"res": "",
			"mat": None,
			"display": "",
			"worn": True,
			"runes": []
		}
	],
	"spellCasters": [
		{
			"name": "Summoner",
			"magicTradition": "divine",
			"spellcastingType": "spontaneous",
			"ability": "cha",
			"proficiency": 2,
			"focusPoints": 0,
			"innate": False,
			"perDay": [
				5,
				2,
				2,
				0,
				0,
				0,
				0,
				0,
				0,
				0,
				0
			],
			"spells": [
				{
					"spellLevel": 0,
					"list": [
						"Stabilize",
						"Divine Lance",
						"Rousing Splash",
						"Protect Companion",
						"Forbidding Ward"
					]
				},
				{
					"spellLevel": 1,
					"list": [
						"Bane",
						"Heal",
						"Magic Weapon"
					]
				},
				{
					"spellLevel": 2,
					"list": [
						"Final Sacrifice",
						"Boneshaker"
					]
				}
			],
			"prepared": [],
			"blendedSpells": []
		}
	],
	"focusPoints": 2,
	"focus": {
		"divine": {
			"cha": {
				"abilityBonus": 3,
				"proficiency": 2,
				"itemBonus": 0,
				"focusCantrips": [
					"Boost Eidolon"
				],
				"focusSpells": [
					"Evolution Surge",
					"Lifelink Surge"
				]
			}
		}
	},
	"formula": [],
	"acTotal": {
		"acProfBonus": 6,
		"acAbilityBonus": 1,
		"acItemBonus": 4,
		"acTotal": 21,
		"shieldBonus": "2"
	},
	"pets": [],
	"familiars": []
})
	# encounter.add_database_monster('Choral')
	encounter.add_database_monster('Ancient Red Dragon')

	# iFrame = InfoFrame(database, root)


	# creature = DatabaseCreature(root, iFrame, creature_json)

	# creature._frame.pack(side = 'left', expand=True, fill=X,)
	# iFrame._frame.pack(expand=True, fill=Y, side='right')

	root.mainloop()	
	
    #I know its uggly but is just a test