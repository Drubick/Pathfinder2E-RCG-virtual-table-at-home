import tkinter as tk
from tkinter import *
from .SlideFrame import SlideFrame

class TextFrame(SlideFrame):

	def __init__(self, info_frame, index, slideInfo = [], font = 'Helvetica 12', font_size = 12) -> None:
		super().__init__(info_frame._frame, index, slideInfo, font, font_size) 
		self._parentFrame =		info_frame
		self._button =			Button(self._parentFrame._frame, text='Back', command=lambda: self._parentFrame.remove_info_slide(self._index))

	def pack(self):
		super().pack()

		# Only show the back button if needed
		if not self._textWidget.compare("end-1c", "==", "1.0"):
			self._button.grid(row=3, sticky='nswe', columnspan=2)

	def pack_forget(self):
		super().pack_forget()
		self._button.grid_forget()

	def handle_event_click(self, event, index):
		if len(self._expand_texts) <= index:
			raise(IndexError('Invalid expanded text index'))
		
		self._parentFrame.add_info_slide(self._expand_texts[index])





if __name__ == '__main__':
	pass