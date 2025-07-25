from PIL import Image, ImageTk

import tkinter as tk


class OverlayWindow:
    '''
    manages the transparent overlay for displaying QR code results
    '''
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw() # start hidden
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.geometry(f'{screen_width}x{screen_height}+0+0')
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes('-topmost', True)
        
        self.overlay_window.attributes('-transparent', True) # might not work with other os
        bg_color = 'systemTransparent'
        
        self.canvas = tk.Canvas(
            self.overlay_window,
            width=screen_width,
            height=screen_height,
            bg=bg_color,
            highlightthickness=0
        )
        self.canvas.pack()
        self.root.bind('<Escape>', self.hide)
        self.canvas.bind('<Button-1>', self.check_click_location)
        
        self.overlay_window.withdraw()
        
        copy_img = Image.open('assets/icon/copy.png').resize((16, 16), Image.Resampling.LANCZOS)
        self.copy_icon = ImageTk.PhotoImage(copy_img)

    def show(self, qr_tuples, scale_factor) -> None:
        '''Makes the overlay visible and draws the results.'''
        self.canvas.delete('all') # clear previous drawings
        
        # draw bounding boxes and info labels
        for data, points in qr_tuples:
            scaled_points = [(p[0] / scale_factor, p[1] / scale_factor) for p in points]
            self.draw_bounding_box(scaled_points)
            self.display_info(data, scaled_points)

        self.overlay_window.deiconify()

    def hide(self, event=None) -> None:
        '''Hides the overlay window.'''
        self.overlay_window.withdraw()
        self.root.withdraw()

    def draw_bounding_box(self, points) -> None:
        '''
        draws a rectangle with rounded corner on canvas
        '''
        min_x = int(min(p[0] for p in points))
        max_x = int(max(p[0] for p in points))
        min_y = int(min(p[1] for p in points))
        max_y = int(max(p[1] for p in points))
        
        self.__create_rounded_rectangle(
            self.canvas,
            min_x, min_y, max_x, max_y,
            outline='lime',
            width=4,
            fill=''
        )

    def display_info(self, data, points) -> None:
        '''
        displays the decoded string and a copy button below a bounding box
        '''
        if not data: return
        
        display_text = (data[:47] + '...') if len(data) > 50 else data
        
        x = min(p[0] for p in points)
        y = max(p[1] for p in points) + 10

        # Create a frame to hold the label and button
        info_frame = tk.Frame(self.canvas, bg='#282828', relief='solid', borderwidth=1)
        
        label = tk.Label(info_frame, text=display_text, fg='white', bg='#282828', padx=5, pady=5)
        label.pack(side=tk.LEFT)
        
        copy_button = tk.Button(
            info_frame,
            image=self.copy_icon,
            command=lambda d=data: self.copy_to_clipboard(d),
            bg='#424242',
            fg='white',
            relief='flat',
            borderwidth=0,
            activebackground='#555555'
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        self.canvas.create_window(x, y, window=info_frame, anchor='nw')

    def copy_to_clipboard(self, text) -> None:
        '''
        copies string to clipboard
        '''
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        print(f'Copied to clipboard: {text}')

    def check_click_location(self, event) -> None:
        '''
        checks if a click was on an empty area of the overlay
        closes the overlay if empty area
        '''
        items = self.overlay_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not items: self.hide()

    def __create_rounded_rectangle(self, canvas, x1, y1, x2, y2, **kwargs) -> int:
        '''
        draws a rectangle with rounded corner on canvas
        '''
        radius = 12
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
