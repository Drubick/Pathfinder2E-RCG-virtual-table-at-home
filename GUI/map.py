from tkinter import ttk, Canvas, filedialog, PhotoImage, Listbox, StringVar
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
    def __init__(self, root, monster_list = None):
        self._monster_list = monster_list
        self._zoom_level = 1.0
        self._frame = ttk.Frame(root)
        self._frame.pack(expand=True, fill='both')
        self._map_image_path = None
        self._top_margin = 10
        self._tokens = {} #dictionary to store the tokens
        self._drag_data = {'x': 0, 'y': 0, 'item': None}#drag data for the tokens
        self._selected_monster = None
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

        self.monster_interface_option()
        


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
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

        self.draw_map()
        for filename in self._tokens.keys():
            self.redraw_tokens()

    def zoom_out(self, event):
        self._zoom_level -= 0.1
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

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

            #Check if there is a selected monster if it is so link it to this token
            linked_monster = self._selected_monster if self._selected_monster is not None else None

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
        
            token_image = self._tokens[filename]['image']
            token_size_width = token_image.width()
            token_size_height = token_image.height()

            x1 = x
            y1 = y
            x2 = x + token_size_width
            y2 = y + token_size_height
            square_item = self._canvas.create_rectangle(x1, y1, x2, y2, outline='red')
            self._tokens[filename]['square'] = square_item



        # The 3 stages of the drag action
        self._canvas.tag_bind(item, "<Button-1>", self.start_drag)
        self._canvas.tag_bind(item, "<B1-Motion>", self.move_token)
        self._canvas.tag_bind(item, "<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        # Convert the canvas coordinates to map coordinates
        x = self._canvas.canvasx(event.x) / self._zoom_level
        y = self._canvas.canvasy(event.y) / self._zoom_level

           # Adjust the coordinates for the zoom level
        adjusted_x = x * self._zoom_level
        adjusted_y = y * self._zoom_level

        # Record the item and its current position
        self._drag_data["item"] = self._canvas.find_closest(adjusted_x, adjusted_y)[0]
        self._drag_data["x"] = x
        self._drag_data["y"] = y

    def start_drag_map(self, event):
        # Convert the canvas coordinates to map coordinates
        x = self._canvas.canvasx(event.x) / self._zoom_level
        y = self._canvas.canvasy(event.y) / self._zoom_level

        # Record the current mouse position
        self._drag_data["x"] = x
        self._drag_data["y"] = y
    
    def move_token(self, event):
        # Convert the canvas coordinates to map coordinates
        x = self._canvas.canvasx(event.x) / self._zoom_level
        y = self._canvas.canvasy(event.y) / self._zoom_level

        # Calculate how much the mouse has moved in canvas coordinates
        dx = (x - self._drag_data["x"]) * self._zoom_level
        dy = (y - self._drag_data["y"]) * self._zoom_level

        # Move the token the same distance as the mouse
        self._canvas.move(self._drag_data["item"], dx, dy)

        # Record the new position
        self._drag_data["x"] = x
        self._drag_data["y"] = y

        # Update the position of the token in the dictionary
        for filename, token in self._tokens.items():
            if token['item'] == self._drag_data["item"]:
                # Adjust the token's position for the zoom level
                token['position'] = (x * self._zoom_level, y * self._zoom_level)
                if 'square' in token:
                    # Move the square the same distance as the mouse
                    self._canvas.move(token['square'], dx, dy)
                break
         
    
    def move_map(self, event):
        # Convert the canvas coordinates to map coordinates
        x = self._canvas.canvasx(event.x) / self._zoom_level
        y = self._canvas.canvasy(event.y) / self._zoom_level

        # Calculate how much the mouse has moved
        delta_x = x - self._drag_data["x"]
        delta_y = y - self._drag_data["y"]

        # Move all items on the canvas
        self._canvas.move("all", delta_x, delta_y)

        # Update the last mouse position
        self._drag_data["x"] = x
        self._drag_data["y"] = y

    def end_drag(self, event):
        # Convert the canvas coordinates to map coordinates
        x = self._canvas.canvasx(event.x) / self._zoom_level
        y = self._canvas.canvasy(event.y) / self._zoom_level

        # Update the position of the token in the dictionary
        for filename, token in self._tokens.items():
            if token['item'] == self._drag_data["item"]:
                token['position'] = (x, y)
                break

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
        for filename in list(self._tokens.keys()):
            # Delete the old token from the canvas
            if self._tokens[filename]['item'] is not None:
                self._canvas.delete(self._tokens[filename]['item'])
                self._tokens[filename]['item'] = None

            # Get the original position of the token
            if 'original_position' not in self._tokens[filename]:
                self._tokens[filename]['original_position'] = self._tokens[filename]['position']
            original_coords = list(self._tokens[filename]['original_position'])

            # Get the current scroll position
            xview = self._canvas.xview()
            yview = self._canvas.yview()

            # Adjust the coordinates based on the zoom level and scroll position
            coords = [(original_coords[0] * self._zoom_level) - xview[0], (original_coords[1] * self._zoom_level) - yview[0]]

            # Resize the image
            image = Image.open(filename)
            if self._grid_scale != 1:
                image = image.resize((int(self._grid_scale), int(self._grid_scale)), Image.ANTIALIAS)
            else:
                image = image.resize((int(self._token_scale * self._zoom_level), int(self._token_scale * self._zoom_level)), Image.ANTIALIAS)

            # Create a new PhotoImage and store it in self._tokens
            photo_image = ImageTk.PhotoImage(image)
            self._tokens[filename]['image'] = photo_image

            # Add the new token to the canvas
            self.add_token(filename, coords[0], coords[1])

    def refresh_monster_interface(self):
        # Clear the Treeview
        for i in self._monster_tree.get_children():
            self._monster_tree.delete(i)

        # Add monsters to the Treeview
        for monster in self._monster_list:
            # Create a label with the monster's name
            monster_name = monster['name']

            # Create a string with the monster's HP
            hp_value = monster['system']['attributes']['hp']['value']
            hp_max = monster['system']['attributes']['hp']['max']
            hp_string = f"HP: {hp_value}/{hp_max}"

            # Add the monster to the Treeview
            self._monster_tree.insert('', 'end', text=monster_name, values=(hp_string,))


    #This method will create the widgets to select the options for the map
    def monster_interface_option(self):
        if hasattr(self, '_monster_tree'):
            return
        # Create a Treeview and a Scrollbar
        self._monster_tree = ttk.Treeview(self._monster_frame)
        scrollbar = ttk.Scrollbar(self._monster_frame, orient="vertical", command=self._monster_tree.yview)
                # Tell the Treeview to scroll with the Scrollbar
        self._monster_tree.configure(yscrollcommand=scrollbar.set)
                # Pack the Treeview and the Scrollbar
        self._monster_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
                # Add monsters to the Treeview
        for monster in self._monster_list:
            # Create a label with the monster's name
            monster_name = monster['name']
                    # Create a string with the monster's HP
            hp_value = monster['system']['attributes']['hp']['value']
            hp_max = monster['system']['attributes']['hp']['max']
            hp_string = f"HP: {hp_value}/{hp_max}"
                    # Add the monster to the Treeview
            self._monster_tree.insert('', 'end', text=monster_name, values=(hp_string,))
                    # Create buttons for changing the monster's stats
        self._monster_tree.bind('<<TreeviewSelect>>', self.on_monster_select)           

    def on_monster_select(self, event):
        # Get the selected item
        selected_item = self._monster_tree.selection()[0]

        selected_index = self._monster_tree.index(selected_item)

        # Update _selected_monster to reference the selected monster
        self._selected_monster = self._monster_list[selected_index]
    
    def change_monster_stats(self, monster):
        # Change the monster's HP
        monster['system']['attributes']['hp']['value'] += change
        self.update_monster_interface()
    
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

        #add a treeview to show the monsters
        self._monster_frame = ttk.Frame(self._frame)
        self._monster_frame.pack(side='left', fill='both')
        
        self.monster_interface_option()
        # Create a new frame on the left side of the root window
      


    
    




