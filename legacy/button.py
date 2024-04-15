from pyglet import sprite, resource, gui
from inspect import signature


class Button(gui.PushButton):

	def __init__(self, name, batch, unpressed_path, pressed_path, hover_path = None, toggle = False) -> None:
		pressed = resource.image(pressed_path)
		unpressed = resource.image(unpressed_path)
		hover = resource.image(hover_path) if hover_path else unpressed

		pressed = sprite.Sprite(pressed, 0,0, batch=batch) #Batch must be the same as the button so it gets loaded into the screen
		pressed.visible = False
		hover = sprite.Sprite(hover, 0,0, batch=batch) #Batch must be the same as the button so it gets loaded into the screen
		hover.visible = False

		super().__init__(0, 0, depressed=unpressed, pressed=pressed, hover=hover, batch=batch)

		self.toggle_mode = toggle
		self.name = name

		unpressed = sprite.Sprite(unpressed, 0,0, batch=batch) #Batch must be the same as the button so it gets loaded into the screen
		unpressed.visible = False

		self._depressed_img = unpressed
		self.on_press = None
		self.on_unpress = None

	def set_on_press(self, funct):
		self.on_press = funct

	def set_on_release(self, funct):
		self.on_release = funct
	
		#Get's a list of parameters
		self.on_release_args = signature(funct).parameters['kwarg1']

	def resize(self, target_width, target_height):

		#Update image size
		self._pressed_img.width = target_width
		self._pressed_img.height = target_height

		self._depressed_img.width = target_width
		self._depressed_img.height = target_height

		self._hover_img.width = target_width
		self._hover_img.height = target_height

		self._sprite.width = target_width
		self._sprite.height = target_height

		#update bounding box
		self._width = target_width
		self._height = target_height

	def move(self, target_x, target_y, target_z = None):

		#Update images 
		if not target_z:
			self._pressed_img.update(target_x, target_y)
		else:
			self._pressed_img.update(target_x, target_y, target_z)

		if not target_z:
			self._depressed_img.update(target_x, target_y)
		else:
			self._depressed_img.update(target_x, target_y, target_z)

		if not target_z:
			self._hover_img.update(target_x, target_y)
		else:
			self._hover_img.update(target_x, target_y, target_z)
		if not target_z:
			self._sprite.update(target_x, target_y)
		else:
			self._sprite.update(target_x, target_y, target_z)


		#update bounding box
		self._x = target_x
		self._y = target_y

		self._sprite.draw()


	def on_mouse_motion(self, x, y):
		self._sprite.visible = False
		but_x, but_y = self._sprite.x, self._sprite.y

		# if not self._pressed:
		if self._check_hit(x, y):
			self._sprite = self._pressed_img if self.toggle_mode and self._pressed \
				else self._hover_img
		else:
			
			self._sprite = self._pressed_img if self._pressed else self._depressed_img

		self._sprite.visible = True
		self._sprite.x, self._sprite.y = but_x, but_y

	def on_mouse_press(self, x, y, arg = None):
		if (self._check_hit(x, y)) :

			#Update button status
			self._pressed = not self._pressed and self.toggle_mode

			if self.toggle_mode:
				if self._pressed and self.on_press:
					self.on_press()
				elif self.on_unpress and self.on_unpress:
					self.execute(self.on_release, self.on_release_args)
			elif self.on_press:
				self.on_press()

			#Update button view
			self.update_view()
			return True
		return False
	
	def update_view(self, set_pressed = None):
			if set_pressed is not None:
				self._pressed = set_pressed

			if self.toggle_mode:
				sprite_to_change = self._pressed_img if self._pressed else self._depressed_img
			else:
				sprite_to_change = self._pressed_img if self._pressed else self._hover_img
			self._sprite.visible = False
			x, y = self._sprite.x, self._sprite.y

			#Update new sprite
			self._sprite = sprite_to_change
			self._sprite.x, self._sprite.y = x, y
			self._sprite.visible = True
