import tkinter as tk
from tkinter import *
from .SlideFrame import SlideFrame

class MonsterFrame(SlideFrame):

	def __init__(self, info_frame, index, slideInfo = [], font = 'Helvetica 12', font_size = 12, monster_list = ()) -> None:
		super().__init__(info_frame._frame, index, slideInfo, font, font_size) 
		self._parentFrame =		info_frame
		self._monster_list = monster_list


	def handle_event_click(self, event, index):
		if len(self._expand_texts) <= index:
			raise(IndexError('Invalid expanded text index'))
	
		self._parentFrame.add_info_slide(self._expand_texts[index])

	def update_monsters(self, monster_list):
		#delete current text
		self._monster_list = monster_list
		for monster in monster_list:
			self.insert_clickable_text(monster + "\n", None)