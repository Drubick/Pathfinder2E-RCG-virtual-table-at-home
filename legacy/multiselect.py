from pyglet import *
from button import Button

class Multi_select(Button):

	def __init__(self, options, width, height, selected, bottom, mid, top, batch) -> None:

		super(Multi_select, self).__init__('Selector', batch, selected, bottom, toggle=True)
		#Load everyhing
		if not options or not len(options):
			raise(Exception('No label options provided!'))


		self.options = []
		for index, option in enumerate(options):
			path = None
			if index != 0:
				path = top if index == len(options) - 1 else mid
			if path:
				image = sprite.Sprite(resource.image(path), self._x, self.y, batch=batch)
				image.width = width
				image.height = height
				image.update(y=self._y + height * index)
				image.visible = False
			else:
				image = None
			label = text.Label(
				option,
				font_name='Times New Roman',
				font_size=12,
				batch=batch,
				x = width / 2,
				y = height / 2 + index * height,
				anchor_x="center",  # Anchor point for X-coordinate ("center" aligns text to the x-coordinate)
				anchor_y="center",  # Anchor point for Y-coordinate ("center" aligns text to the y-coordinate)
			)
			label.visible = False
			
			self.options.append({
				'image': image,
				'label': label
 			})
		self.selected_index = 0
		self.menu_extended = False
		self.options[0]['label'].visible = True

		self.resize(width, height)

		self.max_height = self._height * len(options)
		# self.extended_rectangle.visible = False

	def on_mouse_motion(self, x, y):
		return super().on_mouse_motion(x, y)

	def on_mouse_press(self, x, y, arg=None):
		super().on_mouse_press(x, y, arg)
		if self._pressed and self._x < x < self._x + self._width and self._y < y < self._y + self.max_height:
			pass
		for option in self.options:
			if option['image']:
				option['image'].visible = self._pressed
				option['label'].visible = self._pressed

screen = window.Window()

batch = graphics.Batch()

multist = Multi_select(
		['This is a test', 'Is it really', 'Wow, this is nice'],
		285,
		40,
		"images/icons/gui/multiselect/multiselect_selected.png",
		"images/icons/gui/multiselect/multiselect_bot.png",
		"images/icons/gui/multiselect/multiselect_mid.png",
		"images/icons/gui/multiselect/multiselect_top.png",
		batch
	)

@screen.event
def on_draw():
	screen.clear()
	batch.draw()


@screen.event
def on_mouse_press(x, y, dx, dy):
	multist.on_mouse_press(x, y)
app.run()