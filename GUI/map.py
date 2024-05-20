from tkinter import ttk, Canvas, filedialog, PhotoImage, Listbox
from PIL import Image, ImageTk
import sys


#This class will create a blank grid map or blank map,
#the user can import a map image from a file.
#The user can also add tokens to the map.
#the tokens can be linked via a database to a monster.

#TODO ADD A ROUND COUNTER TO THE INTERFACE
#TODO ADD AN OPTION TO CHANGE THE INITIATIVE ORDER SINCE YOU CAN HOLD YOUR TURN FOR LATER
#AND YOU NOW ARE IN A DIFFERENT SPOT OF THE INITATIVE ORDER
#TODO CHANGE THE LIST SO WHEN IT IS GENERATED IT IS A PROVISIONAL LIST AND HAVE THE OPTION TO MOVE IT TO A FINAL LIST
#INCLUDING AN ADD ALL BUTTON OR SELECT 1 BY 1
class Map:
    def __init__(self, root):
        self._zoom_level = 1.0
        self._frame = ttk.Frame(root)
        self._frame.pack(expand=True, fill='both')
        self._map_image_path = None
        self._top_margin = 10
        self._tokens = {} #dictionary to store the tokens
        self._drag_data = {'x': 0, 'y': 0, 'item': None}#drag data for the tokens
        self._grid_scale = 50  #default square size
        self._token_scale = 30 #default token size
        #creates the widgets to select different options for the map
        self.widgets_option()       

        #Create a canvas to draw the grid
        self._canvas = Canvas(self._frame)
        self._canvas.pack(expand=True, fill='both')

        #bind the draw_grid method to the frame resize event
        self._frame.bind('<Configure>', lambda event: self.draw_grid())
        self._canvas.bind("<Configure>", self.update_grid)
        if sys.platform == "linux":
            self._canvas.bind("<Button-4>", self.zoom_in)
            self._canvas.bind("<Button-5>", self.zoom_out)
        else:
            self._canvas.bind("<MouseWheel>", self.zoom)
            self.bind_events()
        #Adding a draging implementation for when you are zoomed in
        self._canvas.bind("<Button-1>", self.start_drag_map)
        self._canvas.bind("<B1-Motion>", self.move_map)
        self._canvas.bind("<ButtonRelease-1>", self.end_drag_map)
        self._drag_data = {"x": 0, "y": 0}


#This method will draw a grid on the canvas
    def draw_grid(self):
        #get the size of the map
        scrollable_area = self._canvas.bbox("all")
        if scrollable_area is None:
            return
        x1, y1, x2, y2 = scrollable_area

        # Draw the vertical lines
        for i in range(x1, x2, self._grid_scale):
            self._canvas.create_line(i, y1, i, y2, tag='grid')

        # Draw the horizontal lines
        for i in range(y1, y2, self._grid_scale):
            self._canvas.create_line(x1, i, x2, i, tag='grid')

    def update_grid(self, scale):
        self._grid_scale = int(self._grid_scale_combox.get())
        self._canvas.delete('all')
        if self._grid_scale != 1:
            self.draw_grid()
        self.draw_map()
        self.redraw_tokens()

    #This method will allow the user to import a map image from a file
    def import_map(self):
        #open a file dialog to select the image
        filename = filedialog.askopenfilename(filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')])
        if filename:
            self._map_image_path = filename
            self.draw_map()
    
    #TODO ZOOM IN AND OUT USING THE MOUSE WHEEL
    #TODO MOVE MAP AROUND
    def draw_map(self):
        #if there is no image path return
        if self._map_image_path is None:
            return 
        #adjust the size of the image to the canvas
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        #open the image and resize it
        pillow_image = Image.open(self._map_image_path)
        pillow_image = pillow_image.resize((int(canvas_width * self._zoom_level), int(canvas_height * self._zoom_level)))

        #convert the image to a tkinter image since tkinter cant use jpg images
        self._map_image = ImageTk.PhotoImage(pillow_image)
        self._canvas.delete("map")
        self._canvas.create_image(0, 0, image=self._map_image, anchor='nw')
        #redraw the grid if the scale is not 1 (this is in case you want to import a map that allready has a grid drawn into it)
        if self._grid_scale != 1:
            self.draw_grid()

    def zoom_in(self, event):
        self._zoom_level += 0.1
        self.draw_map()
        for filename in self._tokens.keys():
            self.redraw_tokens()

    def zoom_out(self, event):
        self._zoom_level -= 0.1
        self.draw_map()
        for filename in self._tokens.keys():
            self.redraw_tokens()        

    def zoom(self, event):
        if event.delta < 0:
            self._zoom_level += 0.1
        elif event.delta > 0:
            self._zoom_level -= 0.1
        
        print(self._zoom_level)

        # Resize the image
        self.draw_map()
        for filename in self._tokens.keys():
            self.redraw_tokens()
        
        
    #This method will take a image and import it as a token stored in a list
    #a token is a image that can be moved around the map it has an x and y position   
    def import_token(self):
        filename = filedialog.askopenfilename(filetypes=[('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')])
        if filename:
            image = Image.open(filename)
            # Resize the image to the scale of the grid
            if self._grid_scale != 1:
                image = image.resize((self._grid_scale, self._grid_scale), Image.ANTIALIAS)
            else:
                image = image.resize((self._token_scale, self._token_scale), Image.ANTIALIAS)
            photo_image = ImageTk.PhotoImage(image)
            self._tokens[filename] = {'image': photo_image, 'item': None}

        # Add the token to the center of the canvas
        canvas_width = self._canvas.winfo_width()
        canvas_height = self._canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        # Draw the token
        self.add_token(filename, center_x, center_y)
    
    # This method will draw a token on the canvas    
    # TODO RIGHT CLICK ON MONSTER TO GO TO TAB2 AND SHOW MONSTER INFO
    # TODO ADD AN OVERLAY TO SHOW MONSTER TURN, BLUE IF ITS TURN
    # TODO IF THE MONSTER IS DEAD REPLACE TOKEN WITH A DEAD TOKEN
    # TODO IF ITS THE MONSTER TURNS MAKE AN ANIMATION FOR THE BLUE OVERLAY THAT GETS BIGGER AND SMALLER
    # TODO ADD A OVERLAY TO SHOW MONSTER HP IN A COLOR GRADE
    # TODO TOKENS HAVE TO HAVE A LINKED MONSTER
    # TODO MONSTER HAVE A INITIATIVE STAT
    # TODO ADD A SNAP TO GRID AND OPTION TO MOVE WITH ARROW KEYS
    # TODO ADD A NAME BAR ABOVE THE TOKEN
    # TODO WHEN MOVING THE MONSTER WITH THE ARROW KEYS CALCULATE THE DISTANCE AND COMPARE IT TO THE SPEED OF THE MONSTER
    # TODO IF RIGHT CLICK ON MONSTER SHOW DRAW A HEXAGON? AROUND THE MONSTER = O THE SPEED OF THE MONSTER
    # RECOLORING THE GRID TO SHOW THE DISTANCE THE MONSTER CAN MOVE
    # TODO IF I RIGHT CLICK THE MONSTER, IN A RIGHT INTERFACE SHOW STATUS AND MORE INFO OF THE MONSTER
    # TODO AND LET ME CHANGE SOME ATRIBUTES OF THE MONSTER
    def add_token(self, filename, x, y):
        item = None
        if filename in self._tokens:
            item = self._canvas.create_image(x, y, image=self._tokens[filename]['image'], anchor='nw')
            self._tokens[filename]['item'] = item
            self._tokens[filename]['position'] = (x, y)  # Store the position

        # The 3 stages of the drag action
        self._canvas.tag_bind(item, "<Button-1>", self.start_drag)
        self._canvas.tag_bind(item, "<B1-Motion>", self.move_token)
        self._canvas.tag_bind(item, "<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        # Record the item and its current position
        self._drag_data["item"] = self._canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    def start_drag_map(self, event):
    # Record the current mouse position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def move_token(self, event):
        # Calculates how much the mouse has moved
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        # Move the token the same distance as the mouse
        self._canvas.move(self._drag_data["item"], dx, dy)
        # Record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Update the position of the token in the dictionary
        for filename, token in self._tokens.items():
            if token['item'] == self._drag_data["item"]:
                token['position'] = (event.x, event.y)
                break
    def move_map(self, event):
        # Calculate how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # Move all items on the canvas
        self._canvas.move("all", delta_x, delta_y)

        # Update the last mouse position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def end_drag(self, event):
        # Reset the drag data for future usage
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
    
    def end_drag_map(self, event):
        #placeholder in case i want to add anything
        pass
    
    #This method will bind the drag event to the tokens
    def bind_events(self):
        self._canvas.tag_bind("token", "<Button-1>", self.start_drag)
        self._canvas.tag_bind("token", "<B1-Motion>", self.move_token)
        self._canvas.tag_bind("token", "<ButtonRelease-1>", self.end_drag)

    def redraw_tokens(self):
        for filename in list(self._tokens.keys()):  # Use list to avoid 'dictionary changed size during iteration' error
        # Delete the old token from the canvas
            if self._tokens[filename]['item'] is not None:
                coords = self._canvas.coords(self._tokens[filename]['item'])
                self._canvas.delete(self._tokens[filename]['item'])
                self._tokens[filename]['item'] = None
            else:
                coords = [0, 0]
            # Get the position of the token to draw it in the same place
            if 'position' in self._tokens[filename]:
                coords = list(self._tokens[filename]['position'])
            if len(coords) <2:
                coords = [0, 0]
            # Resize the image
            image = Image.open(filename)
            if self._grid_scale != 1:
                image = image.resize((int(self._grid_scale * self._zoom_level), int(self._grid_scale * self._zoom_level)), Image.ANTIALIAS)
            else:
                image = image.resize((int(self._token_scale * self._zoom_level), int(self._token_scale * self._zoom_level)), Image.ANTIALIAS)

            # Create a new PhotoImage and store it in self._tokens
            photo_image = ImageTk.PhotoImage(image)
            self._tokens[filename]['image'] = photo_image

            # Add the new token to the canvas
            canvas_width = self._canvas.winfo_width()
            canvas_height = self._canvas.winfo_height()
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            self.add_token(filename, coords[0], coords[1])

    #This method will create the widgets to select the options for the map
    def widgets_option(self):
        #selects the size of the square grid
        self._grid_scale_label = ttk.Label(self._frame, text="Select the square size of the grid:")
        self._grid_scale_label.pack(anchor='w')
        self._grid_scale_values  = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self._grid_scale_combox = ttk.Combobox(self._frame, values=self._grid_scale_values)
        self._grid_scale_combox.set(self._grid_scale)
        self._grid_scale_combox.bind('<<ComboboxSelected>>', self.update_grid)
        self._grid_scale_combox.pack(anchor='w')

        #imports a map image
        self._import_button = ttk.Button(self._frame, text='Import Map', command=self.import_map)
        self._import_button.pack(anchor='n')
        
        #add tokens to the map
        self._add_token_button = ttk.Button(self._frame, text='Add Token', command=self.import_token)
        self._add_token_button.pack(anchor='n')

        #add a scrollbar
      

        #self._scrollbar.config(command=self._treeview.yview)
        #self._treeview.bind('<Double-1>', self.modify_monster)

     #   self._monster_frame = ttk.Frame(self._frame)
    #    self._monster_frame.pack(side='left', fill='both')

    
    def add_monster(self, name):
        pass
    def modify_monster(self, event):
        pass



