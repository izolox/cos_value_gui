import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

class App:
    def __init__(self, connection):
        self.root = ttk.Window(themename = "darkly")
        self.width = 500
        self.height = 250
        self.creatures = []
        self.search_var = ttk.StringVar()
        
        # crreature info
        self.name = 'Unknown'
        self.value = '0-0'
        self.demand = '0'
        self.stability = 'UNKNOWN'
        
        with connection.cursor() as cursor:
            cr_list = []
            
            cursor.execute("SELECT * FROM creatures;")
            for row in cursor.fetchall():
                cr_list.append(row)
                
            self.creatures = cr_list
        
        self.root.title('Sonaria Creatures')
        self.root.geometry(f'{self.width}x{self.height}')
        self.root.attributes('-topmost', True) # change to remove (True: always on top)
        self.root.resizable(False, False)
        self.root.attributes('-alpha', 0.85)
        
        self.search = ttk.Entry(self.root, textvariable =self.search_var)
        self.search_placeholder = 'Search Creature'
        self.search_var.set(self.search_placeholder)
        self.search.bind('<FocusIn>', lambda e: self.on_search_focus_change('in'))
        self.search.bind('<FocusOut>', lambda e: self.on_search_focus_change('out'))
        self.search.bind('<Return>', lambda e: self.on_search_event('Return'))
        self.search_pos = {'x': 10, 'y': 10, 'width': self.width - (100 - 10), 'height': 25}
        self.search.place(x = self.search_pos['x'], y = self.search_pos['y'], width = self.search_pos['width'], height = self.search_pos['height'])

        
        self.search_button = ttk.Button(self.root, text = 'Search', command = lambda: self.on_search_event('Return'))
        self.s_button_pos = {'x': self.search_pos['x'] + self.search_pos['width'] + 5, 'y': 10, 'width': 100 - 30, 'height': 25}
        self.search_button.place(x = self.s_button_pos['x'], y = self.s_button_pos['y'], width = self.s_button_pos['width'], height = self.s_button_pos['height'])
        
        self.image_box = ttk.Label(self.root)
        self.image_box_pos = {'x': 10, 'y': 45, 'width': 100, 'height': 100}
        self.image_box.place(x = self.image_box_pos['x'], y = self.image_box_pos['y'], width = self.image_box_pos['width'], height = self.image_box_pos['height'])
        
        self.image = Image.open('images/flipli.jpg')
        self.image = ImageTk.PhotoImage(self.image)
        self.image_box.config(image = self.image)
        self.image_box.image = self.image
        
        style = ttk.Style()
        style.configure('White.TLabel', foreground='white')
        
        self.info = ttk.Label(self.root, text = 'Creature Info', style='White.TLabel')
        self.info_pos = {'x': 120, 'y': 35, 'width': 300, 'height': 150}
        self.info.place(x = self.info_pos['x'], y = self.info_pos['y'], width = self.info_pos['width'], height = self.info_pos['height'])
        self.info.config(text = f'Name: {self.name}\nValue: {self.value}\nDemand: {self.demand}/10\nStability: {self.stability}', font = ('Helvitica', 18, 'bold'))
        self.info.config(justify = LEFT, anchor = W)
        
        return self.root.mainloop()
    
    def on_search_focus_change(self, event):
        text = self.search_var.get()
        
        if event == 'out' and text == '':
            self.search_var.set(self.search_placeholder)
        elif event == 'in' and text == self.search_placeholder:
            self.search_var.set('')
            
    def on_search_event(self, event):
        text = self.search_var.get()
        
        if event == 'Return':
            if (text != '') and (text != self.search_placeholder):
                creature = None
                
                for cr in self.creatures:
                    if cr[1].lower().startswith(text.lower()):
                        creature = cr
                        break
                    
                if creature:
                    self.update_info(creature[1], f'{creature[2]}-{creature[3]}', creature[4], creature[5])
        
        self.root.focus_set()
        
    def update_info(self, name, value, demand, stability):
        self.info.config(text = f'Name: {name}\nValue: {value}\nDemand: {demand}/10\nStability: {stability}')
        self.image = Image.open(f'images/{name.lower().replace(" ", "-")}.jpg')
        self.image = ImageTk.PhotoImage(self.image)
        self.image_box.config(image = self.image)
    
    