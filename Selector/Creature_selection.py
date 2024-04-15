from tkinter import *
from tkinter import ttk 
from combat_generator.RCG_logic import Generator
from infoFrame.infoFrame import InfoFrame
from database.bestiary_database import Database
from infoFrame.SlideFrame import SlideFrame
from infoFrame.MonsterFrame import MonsterFrame




class App():
    def generateEncounter(self):
        party_level = int(self._select_party_level.get())
        party_size = int(self._select_party_size.get())
        treath = self._select_threat.get()
        enemy_number = int(self._select_enemy_number.get())

        self._generator.generate(party_size, party_level, treath)
        self._monster_frame.update_monsters([monster['name'] for monster in self._generator._monster_list])

    def displayOptions(self):
        #Select flying monsters
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
        

    def __init__(self, root):

        self._frame = ttk.Frame(root)
        self._database = Database()
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
        self._monster_frame.pack(1,2, 18)
        self._infoFrame._frame.grid(row=0, rowspan= 18, column=1, columnspan=4,sticky='we')


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
