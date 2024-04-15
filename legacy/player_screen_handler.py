from pyglet import *
import json #
from button import Button
import math
from pyglet.window import key as w_key


class PlayerScreen(window.Window):

	def __init__(self, config) -> None:
		display = canvas.get_display()
		screens = display.get_screens()
		
		super(PlayerScreen, self).__init__( screen = screens[config['map_screen']])#fullscreen = True,

		# # STATIC METHODS FUNCTIONS
		# self.static_buttons_mapping = (

		# )

		self.cnfg = config
		self.batch = graphics.Batch()

		# cursor = resource.image(config["cursor"])
		# cursor = window.ImageMouseCursor(cursor, hot_y=cursor.height)
		# self.set_mouse_cursor(cursor)
		# self.cursor_img = sprite.Sprite(resource.image(config["cursor"]))
		# self.cursor_img.visible = False
 
		# setting image as icon
		self.set_icon(resource.image(config["player_screen"]["screen_logo"]))

		# Set background image
		self.background_image = sprite.Sprite(resource.image(self.cnfg['player_screen']['background']), z=-1, batch=self.batch)
		self.background_image.width, self.background_image.height = self.width, self.height

		#Load buttons:
		self.static_buttons = dict()
		required_button_keys = ['pressed', 'unpressed', 'type']

		#Load spotify static buttons
		for name, button_args in self.cnfg['player_screen']['static_buttons'].items():
			allowed = all([False if key not in button_args else True for key in required_button_keys])
			if not allowed:
				print(f'{name} doesn\'t have the required arguments')
				exit(1)
			else:
				if button_args['type'] == 'static' or button_args['type'] == 'toggle':
					for method in self.static_buttons_mapping:
						if method[0] == name:
							if 'size' not in button_args or 'pos' not in button_args:
								print(f'Button {name} doesn\'t have size or pos!')
							else:
								button = Button( #name, mainframe, unpressed_path, pressed_path, hover_path = None, toggle = False
									name,
									self,
									button_args['unpressed'],
									button_args['pressed'],
									hover_path=button_args.get('hover',None),
									toggle=button_args.get('toggle', False)
								)
								button.resize(button_args['size'][0], button_args['size'][1])
								button.move(button_args['pos'][0], button_args['pos'][1])
								button.set_on_press(method[1])
								self.static_buttons[name] = button
							break
					else:
						print('Method not in class static methods!')
		
		self.load_map_guidelines(128)
		self.grid_visibility(False)
		
		# DEBUG LINES
		# self.lines = []
		# for number in (240, 480, 720):
		# 	self.lines.append(shapes.Rectangle(x=number, y=0, width=1, height=self.height, color=(55, 55, 255), batch=self.batch))

		#Event functions are initialized on the CONSTRUCTOR!!!
	
	def on_draw(self):
		self.clear()
		self.batch.draw()
		
		# for line in self.lines:
		# 	line.draw()

	def on_mouse_motion(self, x, y, dx, dy):
		# for button in self.static_buttons.values():
		# 	button.on_mouse_motion(x, y)
		pass

	def on_mouse_press(self, x, y, dx, dy):
		pass
		# for button in self.static_buttons.values():
		# 	if button.on_mouse_press(x, y):
		# 		if button.name in ['prev', 'next'] and not self.static_buttons['play'].button._pressed:
		# 			self.sync_playback_state(True)
		# 			break
		# 		elif button.name not in ['play', 'pause']: # Only pause / play need to keep searching
		# 			break

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if self.grid_line_visible:
			self.grid_with += 4 * scroll_y
			self.grid_with = max(32, self.grid_with)
			self.load_map_guidelines(self.grid_with, offset_x=self.grid_offset_x, offset_y=self.grid_offset_y)

	def on_key_press(self, symbol, modifiers):
		if symbol == w_key.ESCAPE:
			exit()
		elif symbol == w_key.ENTER:
			self.grid_visibility(not self.grid_line_visible)
		elif self.grid_line_visible is not False:
			move_amount = 10
			if modifiers == 1:
				move_amount //= 2
			if symbol in (w_key.UP, w_key.DOWN, w_key.LEFT, w_key.RIGHT):
				if symbol == w_key.UP:
					offset_x, offset_y = 0, move_amount
				elif symbol == w_key.DOWN:
					offset_x, offset_y = 0, -move_amount
				elif symbol == w_key.LEFT:
					offset_x, offset_y = move_amount, 0
				elif symbol == w_key.RIGHT:
					offset_x, offset_y = -move_amount, 0

				# Check and limit grid_offset_x and grid_offset_y
				self.grid_offset_x = max(-self.grid_with, min(self.grid_with, self.grid_offset_x + offset_x))
				self.grid_offset_y = max(-self.grid_with, min(self.grid_with, self.grid_offset_y + offset_y))

				self.move_map_guidelines(offset_x=self.grid_offset_x, offset_y=self.grid_offset_y)


	def move_map_guidelines(self, offset_y = None, offset_x = None):
		for line in self.grid_lines_y:
			if line.anchor_y != offset_y:
				line._anchor_y = offset_y
				line.visible = False
				line.visible = True
		for line in self.grid_lines_x:
			if line.anchor_y != offset_y:
				line._anchor_y = offset_x
				line.visible = False
				line.visible = True

	def load_map_guidelines(self, square_size, line_size=1, offset_x = 0, offset_y = 0):
		self.grid_with = square_size + line_size
		self.grid_offset_y = offset_y
		self.grid_offset_x = offset_x

		square_amount_x = self.width // self.grid_with + 2 # An extra 'grid' for each side
		square_amount_y = self.height // self.grid_with + 2

		# Load x lines
		self.grid_lines_x = []
		for i in range(square_amount_x):
			x = i * self.grid_with - line_size + self.grid_offset_x
			self.grid_lines_x.append(shapes.Line(x, 0, x, self.height, batch=self.batch))

		# Load y lines
		self.grid_lines_y = []
		print(offset_x, offset_y)
		for i in range(square_amount_y):
			y = i * self.grid_with - line_size + self.grid_offset_y
			self.grid_lines_y.append(shapes.Line(0, y, self.width, y, batch=self.batch))

	def grid_visibility(self, visibility):
		self.grid_line_visible = visibility
		for line in self.grid_lines_x:
			line.visible = visibility
		for line in self.grid_lines_y:
			line.visible = visibility

with open('config.json', 'r') as file:
	config = json.load(file)

player_screen = PlayerScreen(config)

app.run()