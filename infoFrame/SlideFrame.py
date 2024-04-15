import tkinter as tk
from tkinter import *

class SlideFrame():

	def __init__(self, frame, index = 0, slideInfo = [], font = 'Helvetica 12', font_size = 12, standalone = False) -> None:
		self._scrollbar =		Scrollbar(frame)
		self._standalone =		False
		self._index =			index
		self._font =			font
		self._textWidget =		tk.Text(
			frame,
			width=10,
			font=font,
			padx=12,
			pady=12,
			yscrollcommand=self._scrollbar.set
		)
		self._expand_texts =	[]
	
		self._scrollbar.config(command=self._textWidget.yview)

		# Disables all text related events (i.e: selecting text, double clicking to select the current word...)
		self._textWidget.bindtags((str(self._textWidget), str(frame), "all"))

		self._textWidget.config(wrap=WORD)

		# This tag makes the clickable text bold and italic
		self._textWidget.tag_configure("bold", font=f"{font} bold")
		self._textWidget.tag_configure("bold_italic", font=f"{font} bold italic")
		self._textWidget.tag_configure("bigger_line_jump", font=f"{font}")

		for text_chunk in slideInfo:
			if not text_chunk['expandable']:
				self.insert_normal_text(text_chunk['text'])
			else:
				self.insert_clickable_text(text_chunk['text'], text_chunk['expand_text'])

	def insert_normal_text(self, text, pos = 'end', tags = None):
		self._textWidget.insert(pos, text, tags)

	def insert_image(self, img):
		self._textWidget.image_create(tk.END, image = img)

	def pack(self, row = 2, column=0, rowspan=1, columnspan=1, sticky='nswe'):
		self._textWidget.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky)
		self._scrollbar.grid(row=row, column=column+1, rowspan=rowspan, sticky='nswe')

	def pack_forget(self):
		self._textWidget.grid_forget()
		self._scrollbar.grid_forget()

	def insert_clickable_text(self, text, expand_text):

		#Get the index and add to the list
		index = len(self._expand_texts)
		self._expand_texts.append(expand_text)

		#Create tag for this element
		expand_tag = f'expand_{index}'
		self._textWidget.tag_configure(expand_tag)
		
		#Configure tag event
		self._textWidget.tag_bind(expand_tag, '<1>', lambda event, arg=index: self.handle_event_click(event, arg))
		
		#Add text to the textWidget, with the required tags
		self._textWidget.insert("end", text, ("bold_italic", expand_tag))

	def handle_event_click(self, event, index):
		pass





if __name__ == '__main__':
	pass