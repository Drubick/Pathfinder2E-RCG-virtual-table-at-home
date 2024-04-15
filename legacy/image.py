import tkinter as tk
from tkinter import filedialog
import pygame.image
import re

def query_file(file_types = ()):
	root = tk.Tk()
	root.withdraw()

	file_path = filedialog.askopenfilename(filetypes=file_types)
	return file_path

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    #new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image

def scale(surface, factor = None, factor_x = None, factor_y = None):
	if any((factor, factor_x, factor_y)):
		size_x, size_y = surface.get_rect().size
		if factor:
			size_x *= factor
			size_y *= factor
		else:
			if factor_x:
				size_x *= factor_x
			if factor_y:
				size_y *= factor_y
		surface = pygame.transform.scale(surface, (size_x, size_y))
	return surface


def load_image(path = None):
	if path is None:
		path = query_file()

	try:
		image = pygame.image.load(path)
		return image
	except:
		print('Couldn\'t open the image!')
	return None

def render_text(screen, text, pos, colour = (0, 0, 0), size = 15):
	myfont = pygame.font.SysFont("monospace", size)
	label = myfont.render(text, 1, colour)
	screen.blit(label, pos)