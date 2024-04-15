import tkinter as tk
from tkinter import *
from tkinter import ttk
from database import *

from .TextFrame import TextFrame

class InfoFrame():

	def __init__(self, database: Database, master, font = 'Helvetica 12') -> None:
		self._database = database
		self._frame = Frame(master, borderwidth=1, border=1)
		self._infoFrames = []
		self._font = font
		self._placeholder = TextFrame(self, 0, font=font)
	
		search_categories = [option.capitalize() for option in self._database.database_references.keys()]
		self.search_categories = ttk.Combobox(self._frame, state='readonly', values = search_categories)
		self.search_categories.bind("<<ComboboxSelected>>", self.category_changed)
		
		self.search_options = ttk.Combobox(self._frame, state='readonly', values = [])
		self.search_options.bind("<<ComboboxSelected>>", self.option_changed)
		self.search_dict = {}

		# Configure the grid
		self._frame.grid_configure(padx=10)
		self._frame.columnconfigure(0, weight=9)
		self._frame.columnconfigure(0, weight=1)
		self._frame.rowconfigure((0,1,3), weight=1)
		self._frame.rowconfigure(2, weight=100)

		# Grid the search categories
		self.search_categories.grid(row=0, column=0, columnspan=2, sticky='nswe')
		self.search_options.grid(row=1, column=0, columnspan=2, sticky = 'nswe')
		self.update_view()

	def category_changed(self, event = None):
		selected_category = self.search_categories.get()

		if selected_category:
			if selected_category not in self.search_dict:
				category_options = self._database.get_table_element_names(selected_category.lower())
				self.search_dict[selected_category] = category_options
			
			self.search_options['values'] = self.search_dict[selected_category]
			self.search_options.set('')

	def option_changed(self, event = None):
		name =					self.search_options.get()
		category =				self.search_categories.get()

		if name and category:
	
			data_to_extract =	f"json_extract(data, '$.system.description.value')"
			query =				f'SELECT {data_to_extract} FROM "{category.lower()}" WHERE json_extract(data, "$.name") = \"{name}\" LIMIT 1;'
			option_text =		self._database.search(query)[0]

			self.add_info_slide(option_text, category, name)

	def update_view(self):
		if len(self._infoFrames):
			option =	self._infoFrames[-1]['option']
			category =	self._infoFrames[-1]['category']

			self._infoFrames[-1]['frame'].pack()
		else:
			option =	''
			category =	''

			self._placeholder.pack()

		#The list updates itself automatically cause events
		self.search_options.set(option)
		self.search_categories.set(category)

	def _remove_last_slide(self):
		if self._infoFrames:
			self._infoFrames[-1]['frame'].pack_forget()
		else:
			self._placeholder.pack_forget()

	def add_info_slide(self, rawText = None, slide = None, category = '', option = ''):
		#Update the view

		if rawText:
			slide_info = self._database.extract_reference(rawText)
			if slide_info:
				self._remove_last_slide()
				self._infoFrames.append({
					'frame': TextFrame(self, len(self._infoFrames), slide_info),
					'category': category,
					'option': option
				})
			else:
				print('Couldn\'t find database reference!')
				return
		elif slide:
			if not slide._textWidget.compare("end-1c", "==", "1.0"):
				self._remove_last_slide()
				self._infoFrames.append({
					'frame': slide,
					'category': '',
					'option': ''
				})
			else:
				print('Attempted to add an empty slide!')
				return
		else:
			return
		self.update_view()

	def remove_info_slide(self, index = None):
		if not index:
			index = -1
			if not len(self._infoFrames):
				return
		else:
			if index >= len(self._infoFrames):
				raise(IndexError('Invalid index!'))
		#Remove current slide
		self._infoFrames[index]['frame'].pack_forget()
		del self._infoFrames[index]
		self.update_view()

if __name__ == '__main__':
	root = Tk()
	root.geometry('500x500')
	database = Database('bestiary.db')
	info_frame = InfoFrame(database, root)
	source_text = '''<section class="fumble-deck">
<h1>Wait, What?</h1>
<blockquote>
<p>You are @UUID[Compendium.pf2e.conditionitems.Item.Confused]</p>
</blockquote>
<p><code>Melee</code></p>
<h1>Don't hit Me!</h1>
<blockquote>
<p>Until the end of your next turn, each time you miss with a ranged attack targeting enemy adjacent to any of your allies, you hit one of those adjacent allies instead (determined randomly by the GM).</p>
</blockquote>
<p><code>Ranged</code></p>
<h1>Pinched Nerve</h1>
<blockquote>
<p>Until healed, you take a @UUID[Compendium.pf2e.other-effects.Item.Effect: -10-foot circumstance penalty to your land Speed]{-10-foot circumstance penalty to your land Speed} and are @UUID[Compendium.pf2e.conditionitems.Item.Clumsy]{Clumsy 1}.</p>
</blockquote>
<p><code>Unarmed</code></p>
<h1>Mental Slip</h1>
<blockquote>
<p>You are @UUID[Compendium.pf2e.conditionitems.Item.Controlled] by the target until the end of your next turn.</p>
</blockquote>
<p><code>Spell</code></p>
</section>
'''
	info_frame.add_info_slide(source_text)
	info_frame._frame.pack(expand=True, fill='both')

	root.mainloop()	