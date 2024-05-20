from tkinter import *
from tkinter import ttk 
from combat_generator.RCG_logic import Generator
from infoFrame.infoFrame import InfoFrame
from database.bestiary_database import Database
from infoFrame.SlideFrame import SlideFrame
from infoFrame.MonsterFrame import MonsterFrame
from database import *


#This is a class that creates a tkinter interface displayed in a 3 column grid, that it allows the user
#to search for different items in the database (primary monsters), and display them in the middle column.
#it will also store the finded items in a list that can be used later.(the list is a dictionary of json objects)
class Item_search():
    #This method will show the items in the middle column of the interface
    def show_items(self, item_list):
        self._monster_frame.update_monsters([item['name'] for item in item_list])

    #This method will generate an encounter based on the user input, 
    #it will store the monsters in a list that can be used later and display the monsters in the middle column    
    #TODO: check for errors, sometimes this function will not work as intended
    def generateEncounter(self):
        party_level = int(self._select_party_level.get())
        party_size = int(self._select_party_size.get())
        treath = self._select_threat.get()
        enemy_number = int(self._select_enemy_number.get())

        self._generator.generate(party_size, party_level, treath)
        self.show_items(self._generator._monster_list)
        self._monster_list += self._generator._monster_list
        
#When this method is called it will create an expandable option menu that will allow the user to select the traits of the monster he wants to search for.
#it will also create a button that will call the search method. allowing to search in the database
    def displayOptions(self):
        #Select flying monsters
        self._search=ttk.Button(self._frame, text='Search', command=self.search)
        self._search.grid(row=14,column=0, sticky='W')

        self._can_fly = BooleanVar()
        self._text_fly = ttk.Label(self._frame, text='The monster can fly')
        self._text_fly.grid(row=8,column=0, sticky='N')
        self._fly_true = Radiobutton(self._frame, text="Yes", variable = self._can_fly, value=True)
        self._fly_true.grid(row=8, column=0, sticky='WS')
        self._fly_false = Radiobutton(self._frame, text="No", variable = self._can_fly, value=False)
        self._fly_false.grid(row=8, column=0, sticky='ES')
        #Select swiming monsters
        self._can_swim = BooleanVar()
        self._text_swim = ttk.Label(self._frame, text='The monster can swim')
        self._text_swim.grid(row=10,column=0, sticky='N')
        self._swim_true = Radiobutton(self._frame, text="Yes", variable = self._can_swim, value=True)
        self._swim_true.grid(row=10, column=0, sticky='WS')
        self._swim_false = Radiobutton(self._frame, text="No", variable = self._can_swim, value=False)
        self._swim_false.grid(row=10, column=0, sticky='ES')
        #Select darkvision monster
        self._has_darkvision = BooleanVar()
        self._text_darkvision = ttk.Label(self._frame, text='The monster has darkvision')
        self._text_darkvision.grid(row=11,column=0, sticky='N')
        self._darkvision_true = Radiobutton(self._frame, text="Yes", variable = self._has_darkvision, value=True)
        self._darkvision_true.grid(row=11, column=0, sticky='WS')
        self._darkvision_false = Radiobutton(self._frame, text="No", variable = self._has_darkvision, value=False)
        self._darkvision_false.grid(row=11, column=0, sticky='ES')
        #Select "magic monster"(the monster can use spells)
        self._can_spellcast = BooleanVar()
        self._text_spellcast = ttk.Label(self._frame, text='The monster can cast spells')
        self._text_spellcast.grid(row=12,column=0, sticky='N')
        self._spellcast_true = Radiobutton(self._frame, text="Yes", variable = self._can_spellcast, value=True)
        self._spellcast_true.grid(row=12, column=0, sticky='WS')
        self._spellcast_false = Radiobutton(self._frame, text="No", variable = self._can_spellcast, value=False)
        self._spellcast_false.grid(row=12, column=0, sticky='ES')
        #select monster with special saves
        self._special_saves = BooleanVar()
        self._special_saves = ttk.Label(self._frame, text='The monster has special saves')
        self._special_saves.grid(row=13,column=0, sticky='N')
        self._special_saves_true = Radiobutton(self._frame, text="Yes", variable = self._special_saves, value=True)
        self._special_saves_true.grid(row=13, column=0, sticky='WS')
        self._special_saves_false = Radiobutton(self._frame, text="No", variable = self._special_saves, value=False)
        self._special_saves_false.grid(row=13, column=0, sticky='ES')

#This method allows the user to search for a monster with specific traits in the database.
#TODO simplifly the code by extrapolating the can_fly can_swim etc. to a list of traits or 
#TODO something similar and use the getters in the same method where they are created if possible
    def search(self):
        query = Query("monsters")
        query.add_source_filter('pathfinder-bestiary')
        query.limit = 1
        can_fly = self._can_fly.get() 
        can_swim = self._can_swim.get()
        has_darkvision = self._has_darkvision.get()
        can_spellcast = self._can_spellcast.get()
       # special_saves = self._special_saves.get()
        query.add_filter([MON.other_speed, '=' if can_fly else '!='  ,'fly'])
        query.add_filter([MON.other_speed, '=' if can_swim else '!='  ,'swim'],               previous_content_operator = SQL_OP.AND)
        query.add_filter([MON.sense, '=' if has_darkvision else '!='  ,'darkvision'],               previous_content_operator =  SQL_OP.AND)
        query.add_filter([MON.spellcaster, '=' if can_spellcast else '!='  ,'spellcastingEntry'],  previous_content_operator =  SQL_OP.AND)
        #query.add_filter([MON.special_saves, '!=' if special_saves else '='  ,' '],                 previous_content_operator =  SQL_OP.AND)
        
        #Creating a list of monsters, first empty in case we dont find anything
        monster_list = []
        monster_list += self._database.search(query.compose_query())

        self.show_items(monster_list)
        self._monster_list += monster_list

#TODO further separate the init into functions, so the interface is not generated at the calling
#of the class and the class can be used in a more modular way, (maybe create a function that generates the interface)??
    def __init__(self, root):

        self._frame = ttk.Frame(root)
        self._frame.pack(expand=True, fill='both')
        self._database = Database()
        self._monster_list = []
        self._frame.grid_columnconfigure(0, weight = 2)
        self._frame.grid_columnconfigure(1, weight = 7)
        self._frame.grid_columnconfigure(2, weight = 2)
        
        self._frame.grid_rowconfigure(0,    weight = 1)
        self._frame.grid_rowconfigure(tuple(range(20)),    weight = 1)

 
        self._generator = Generator()
        #Widgets
        #select the avarage level of the party
        self._party_lvl = ttk.Label(self._frame, text='Party Level')
        self._select_party_level = ttk.Combobox(self._frame, width=10)
        self._select_party_level['values'] = tuple(range(20))
        #select the size of the party
        self._party_size = ttk.Label(self._frame, text='Party Size') 
        self._select_party_size = ttk.Combobox(self._frame, width=10)
        self._select_party_size['values'] = (1,2,3,4,5,6,7,8,9)
        #Select the difficulty of the fight
        self._threat = ttk.Label(self._frame,text=('Threat Level'))
        self._select_threat = ttk.Combobox(self._frame, width=10)
        self._select_threat['values'] = ('Trivial', 'Low', 'Moderate', 'Severe', 'Extreme')
        #Select the number of enemies in the encounter
        self._enemy_number =ttk.Label(self._frame, text =('Introduce number of enemies'))
        self._select_enemy_number = ttk.Entry(self._frame)
        #show widgets
        self._party_lvl.grid(row = 0,column = 0, sticky='NSWE')
        self._select_party_level.grid(row = 1, column = 0, sticky='NWE')

        self._party_size.grid(row = 2, column = 0, sticky= 'NSWE')
        self._select_party_size.grid(row = 3, column = 0, sticky='NWE')
       
        self._threat.grid(row = 4, column = 0, sticky= 'NSWE')
        self._select_threat.grid(row =5, column = 0, sticky = 'NWE')

        self._enemy_number.grid(row = 6, column=0, sticky= 'NSWE')
        self._select_enemy_number.grid(row=7, column=0, sticky='NWE')

        self._button = ttk.Button(self._frame, text='Generate', command=self.generateEncounter)
        self._button.grid(row=0,column=1, sticky='W')

        self._display_options  = ttk.Button(self._frame, text='More options', command= self.displayOptions)
        self._display_options.grid(row=7,column=0,sticky='s')

        #column1
        #this will show the different monsters generated
        self._infoFrame = InfoFrame(self._database, self._frame)
        self._monster_frame = MonsterFrame(self._infoFrame,0)
        self._monster_frame.pack()
        self._infoFrame._frame.grid(row=0, rowspan=10, column=1, columnspan=1,sticky='we')#


        #main setup
        
        


        #slide of the different traits a monster can have EX:amphibious dragon evil...
        #self._monster_traits
        #self._monster_rarity
        #self._monster_size
        #self._spoken_languages
        #self._inmunities
        #self._monster_level
        #SUPERSPECIFIC THINGS (should we even include this?)
        #self._lores
