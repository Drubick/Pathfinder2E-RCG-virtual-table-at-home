from tkinter import ttk, Canvas, filedialog, PhotoImage
from PIL import Image, ImageTk


#This class will create a blank grid map or blank map,
#the user can import a map image from a file.
#The user can also add tokens to the map.
#the tokens can be linked via a database to a monster.
class Map:
    def __init__(self, root):
        self._frame = ttk.Frame(root)
        self._frame.pack(expand=True, fill='both')
        self._map_image_path = None
        self._top_margin = 10
        #default square size
        self._scale = 50
        
        #creates the widgets to select different options for the map
        self.widgets_option()       

        #Create a canvas to draw the grid
        self._canvas = Canvas(self._frame)
        self._canvas.pack(expand=True, fill='both')

        #bind the draw_grid method to the frame resize eve
        self._frame.bind('<Configure>', lambda event: self.draw_grid())
        self._canvas.bind("<Configure>", self.update_grid)


#This method will draw a grid on the canvas
    def draw_grid(self):
        #get the size of the frame
        width = self._frame.winfo_width()
        height = self._frame.winfo_height()

        #get the size of the square grid
        square_size = int(self._scale)

        #calculate the number of squares in the x and y axis
        x_squares = width // square_size
        y_squares = (height - self._top_margin) // square_size

        #draw the grid
        for x in range(x_squares):
            for y in range(y_squares):
                x1= x * square_size
                y1= y * square_size + self._top_margin
                x2= x1 + square_size
                y2= y1 + square_size
                self._canvas.create_rectangle(x1, y1, x2, y2)

    def update_grid(self, scale):
        self._scale = int(self._scale_combox.get())
        self._canvas.delete('all')
        if self._scale != 1:
            self.draw_grid()
        self.draw_map()

    def import_map(self):
        filename = filedialog.askopenfilename(filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')])
        if filename:
            self._map_image_path = filename
            self.draw_map()
    
    def draw_map(self):
        if self._map_image_path is None:
            return 
        if self._scale == 1:
            self._canvas.delete('all')
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        pillow_image = Image.open(self._map_image_path)
        pillow_image = pillow_image.resize((canvas_width, canvas_height))
        self._map_image = ImageTk.PhotoImage(pillow_image)
        self._canvas.delete("map")
        self._canvas.create_image(0, 0, image=self._map_image, anchor='nw')
        if self._scale != 1:
            self.draw_grid()  # Call draw_grid after create_image

#This method will create the widgets to select the options for the map
    def widgets_option(self):
        #selects the size of the square grid
        self._scale_label = ttk.Label(self._frame, text="Select the square size of the grid:")
        self._scale_label.pack(anchor='w')
        self._scale_values  = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._scale_combox = ttk.Combobox(self._frame, values=self._scale_values)
        self._scale_combox.set(self._scale)
        self._scale_combox.bind('<<ComboboxSelected>>', self.update_grid)
        
        self._scale_combox.pack(anchor='w')

        #imports a map image
        self._import_button = ttk.Button(self._frame, text='Import Map', command=self.import_map)
        self._import_button.pack(anchor='n')



