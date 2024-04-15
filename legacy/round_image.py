import pyglet
from PIL import Image
import math
import io

def is_point_inside_circle(x, y, width, height):
	# Calculate the center of the rectangle
	center_x = width / 2
	center_y = height / 2
	
	# Calculate the radius as half of the smallest dimension
	radius = min(width, height) / 2
	
	# Calculate the distance between the point and the circle's center
	distance = int(math.sqrt((x - center_x)**2 + (y - center_y)**2))
	
	# Check if the distance is less than or equal to the radius
	return distance <= radius

def index_to_xy(index, width, height):
	if index < 0 or index >= width * height:
		raise ValueError("Index is out of bounds")

	x = index % width
	y = index // width

	return x, y

def index_to_xy(index, width, height):
	if index < 0 or index > width * height:
		raise ValueError("Index is out of bounds")

	x = index % width
	y = index // width

	return x, y

image_path = 'images/icons/gui/playlists/battle.jpg'

img = Image.open(image_path)
img = img.convert("RGBA")

pixdata = img.load()

width, height = img.size
for y in range(height):
	for x in range(width):
		if  not is_point_inside_circle(x, y, width, height):
			pixdata[x, y] = (255, 255, 255, 0)

img.save(image_path, "PNG")