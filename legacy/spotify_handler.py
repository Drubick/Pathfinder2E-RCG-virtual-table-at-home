from audio import Spotify
from pyglet import *
import json #
from button import Button
import math

class SpotifyHandler(window.Window):

	def __init__(self, config) -> None:
		super(SpotifyHandler, self).__init__(style=window.Window.WINDOW_STYLE_BORDERLESS)
		self.spotify = Spotify(config['client_id'], config['client_secret'])

		# STATIC METHODS FUNCTIONS
		self.static_buttons_mapping = (
			('play', self.spotify.play),
			('pause', self.spotify.pause),
			('next', self.spotify.next),
			('prev', self.spotify.prev),
			('playlist_next', self.move_playlist_right),
			('playlist_prev', self.move_playlist_left)
		)
		
		player_info = self.spotify.get_current_player_info()

		if not player_info: # If no player available, exit...
			exit(1)

		self.cnfg = config
		self.batch = graphics.Batch()

		display = canvas.get_display()
		screens = display.get_screens()
 
		# setting image as icon
		self.set_icon(resource.image(config["spotify_logo"]))

		cursor = resource.image(config["cursor_inv"])
		cursor = window.ImageMouseCursor(cursor, hot_y=cursor.height, acceleration=True)
		self.set_mouse_cursor(cursor)
		self.cursor_img = sprite.Sprite(resource.image(config["cursor"]))
		# self.set_mouse_visible(False)
		# self.set_mouse_platform_visible(False)

		# Set background image
		self.background_image = sprite.Sprite(resource.image(self.cnfg['spotify_screen']['spotify_background']), z=-1, batch=self.batch)
		self.background_image.width, self.background_image.height = self.width, self.height

		#Load buttons:
		self.static_buttons = dict()
		self.playlist_buttons = []
		required_spotify_keys = ['pressed', 'unpressed', 'type'] 


		#Load spotify static buttons
		for name, button_args in self.cnfg['spotify_screen']['spotify_buttons'].items():
			allowed = all([False if key not in button_args else True for key in required_spotify_keys])
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
									self.batch,
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

		self.sync_playback_state(player_info['is_playing'])

		#Set playback to random pick
		self.spotify.shuffle(True)

		# Playlist buttons handling
		if 'playlist_buttons' in self.cnfg['spotify_screen']:
			for name, button_args in self.cnfg['spotify_screen']['playlist_buttons'].items():
				required_playlist_keys = ['playlist_id', 'icon']
				allowed = all([False if key not in button_args else True for key in required_playlist_keys])
				if not allowed:
					print(f'{name} doesn\'t have the required arguments')
					exit(1)
				else:
					if 'playlist_id' not in button_args:
						print(f'Playlist {name} doesn\'t have a playlist!')
						exit(1)
					else:
						button_args.update({
							'border': self.cnfg['spotify_screen']['playlist_frame'],
							'name': name
						})
						self.playlist_buttons.append(Playlist_button(button_args, self.spotify, self.batch))
						self.playlist_buttons[-1].hide()
			#Prepare playlist buttons to work on screen
			self.pl_indexes = (-1, 0, 1)
			self.repostition_playlist_buttons()

		if self.cnfg['dm_screen'] >= len(screens) + 1:
			self.cnfg['dm_screen'] = 0

		# Update screen position
		screen_y = screens[self.cnfg['dm_screen']].height - self.height
		screen_x = screens[self.cnfg['dm_screen']].width - self.width + 40
		self.set_location(screen_x, screen_y)

		# DEBUG LINES
		# self.lines = []
		# for number in (240, 480, 720):
		# 	self.lines.append(shapes.Rectangle(x=number, y=0, width=1, height=self.height, color=(55, 55, 255), batch=self.batch))

		#Event functions are initialized on the CONSTRUCTOR!!!
	
	def on_mouse_enter(self, x, y):
		self.cursor_img.visible = True

	def on_mouse_leave(self, x, y):
		self.cursor_img.visible = False
	
	def on_draw(self):
		self.clear()
		self.batch.draw()
		if self.cursor_img.visible:
			self.cursor_img.draw()
		
		# for line in self.lines:
		# 	line.draw()

	def on_mouse_motion(self, x, y, dx, dy):
		self.cursor_img.update(x, y)
		for button in self.static_buttons.values():
			button.on_mouse_motion(x, y)
		pass

	def on_mouse_press(self, x, y, dx, dy):
		for button in self.static_buttons.values():
			if button.on_mouse_press(x, y):
				if button.name in ['prev', 'next'] and not self.static_buttons['play']._pressed:
					self.sync_playback_state(True)
					break
				elif button.name not in ['play', 'pause']: # Only pause / play need to keep searching
					break
		for button in self.playlist_buttons:
			if button.on_mouse_press(x, y) and not self.static_buttons['play']._pressed:
				# Set play/pause to play
				self.sync_playback_state(True)

	def sync_playback_state(self, is_playing):
			self.static_buttons['play'].update_view(set_pressed=is_playing)
			self.static_buttons['pause'].update_view(set_pressed=not is_playing)

	def get_playlist_indexes(self, current_index):
		if len(self.playlist_buttons) == 1:
			return tuple(0)
		


		prev_playlist = current_index - 1
		next_playlist = current_index + 1 
		next_playlist =  next_playlist if current_index  + 1 < len(self.playlist_buttons) else 0

		if len(self.playlist_buttons) == 2: # Only two playlists
			return (current_index, next_playlist)

		return (prev_playlist, current_index, next_playlist)

	def repostition_playlist_buttons(self):
		if not len(self.playlist_buttons):
			return
		elif len(self.playlist_buttons) == 1:
			new_button_x = self.width // 2 - self.playlist_buttons[0].width / 2
			new_button_y = self.height // 2 - self.playlist_buttons[0].height / 2
			self.playlist_buttons[0].move(new_button_x, new_button_y)
		
			self.playlist_buttons[0].show()
			return
		else:
			if not hasattr(self, 'pl_separation'):
				self.pl_separation = self.width // ( 1 + min(len(self.playlist_buttons), 3))
				self.pl_y = self.height // 2 - self.playlist_buttons[0].height //2
				self.selected_pl_index = 0

			for number, index in enumerate(self.pl_indexes):
				self.playlist_buttons[index].show()
				move_x = (number + 1) * self.pl_separation - self.playlist_buttons[index].width // 2
				self.playlist_buttons[index].move(move_x, self.pl_y)

	def move_playlist_right(self):
		target_index =  self.pl_indexes[1] + 1
		target_index = target_index if target_index < len(self.playlist_buttons) else 0

		for index in self.pl_indexes:
			self.playlist_buttons[index].hide()

		self.pl_indexes =  self.get_playlist_indexes(target_index)
		self.repostition_playlist_buttons()

	def move_playlist_left(self):
		target_index =  self.pl_indexes[1] - 1
		target_index = target_index if target_index > 0 else len(self.playlist_buttons) - 1

		for index in self.pl_indexes:
			self.playlist_buttons[index].hide()

		self.pl_indexes =  self.get_playlist_indexes(target_index)
		self.repostition_playlist_buttons()

class Playlist_button():

	def __init__(self, data, sp_handler: SpotifyHandler, batch) -> None:
		self._data = data
		self._x = 0
		self._y = 0
		self.visible = True

		self._icon = sprite.Sprite(resource.image(data['icon']), batch=batch)
		self._border = sprite.Sprite(resource.image(data['border']), batch=batch)
		self.playlist = f'spotify:playlist:{data["playlist_id"]}'
		self.name = data['name']
		self.sp_handler = sp_handler

		self.resize(200, 200)
		self.width = 200
		self.height = 200
	
	def resize(self, target_width, target_height):
		self._border.width, self._border.height = target_width, target_height
		self.width = target_width
		self.height = target_height
		#_icon should be % smaller
		self._icon.width, self._icon.height = target_width, target_height

	def move(self, target_x, target_y):
		self._border.update(target_x, target_y)
		self._icon.update(target_x, target_y)
		self._x = target_x
		self._y = target_y

	def hide(self):
		self._border.visible = False
		self._icon.visible = False

	def show(self):
		self._border.visible = True
		self._icon.visible = True

	def on_mouse_press(self, x, y):
		if (x > self._x and x <= self._x + self.width and
      		y > self._y and y <= self._y + self.height):
			return self.sp_handler.play(self.playlist)
		return False



with open('config.json', 'r') as file:
	config = json.load(file)

sp_struct = SpotifyHandler(config)

app.run()