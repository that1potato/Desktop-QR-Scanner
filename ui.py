import tkinter as tk


class UI:
    def __init__(self, root, qr_scanner) -> None:
        self.root = root
        self.scanner = qr_scanner
        self.overlay_window = None
        self.overlay_canvas = None
        self.root.title('QR Code Scanner')
        self.root.geometry('500x200')
        self.corner_radius = 12
        
        main_label = tk.Label(
            self.root,
            text='Press Cmd+Shift+1 to scan for QR codes.\nPress Esc to close overlay.'
        )
        main_label.pack(pady=40, padx=20)
        
        scan_button = tk.Button(
            self.root,
            text= 'Scan',
            command=self.scan_and_display
        )
        scan_button.pack(pady=10)
        
        self.root.bind('<Command-Shift-1>', self.scan_and_display)
    
    def scan_and_display(self, event=None) -> None:
        '''
        scans the qrcode and display the overlay
        '''
        print('scanning...')
        # detect & decode
        self.scanner.take_screenshot()
        
        # get scale factor
        physical_width = self.scanner.screenshot_frame.shape[1]
        logical_width = self.root.winfo_screenwidth()
        scale_factor = physical_width / logical_width
        print(f'Physical width: {physical_width}, Logical width: {logical_width}, Detected Scale Factor: {scale_factor}')
        
        ok, data, points, _ = self.scanner.detect_decode_multi()
        if not ok:
            print('No QR code detected.')
            self.close_overlay()
        else:
            print(f'Found {len(data)} QR code(s): {data}')
            # adjust for high dpi
            scaled_points = [
                [(p[0] / scale_factor, p[1] / scale_factor) for p in point_array] 
                for point_array in points
            ]
            qr_tuples = list(zip(data, scaled_points))
            
            self.open_overlay()
            self.draw_bounding_boxes(qr_tuples)
            self.display_info(qr_tuples)
    
    def open_overlay(self) -> None:
        '''
        opens the overlay to draw on
        '''
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.destroy()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.geometry(f'{screen_width}x{screen_height}+0+0')
        self.overlay_window.overrideredirect(True)
        self.overlay_window.attributes('-topmost', True)
        
        self.overlay_window.attributes('-transparent', True) # might not work with other os
        bg_color = 'systemTransparent'
        
        self.overlay_canvas = tk.Canvas(
            self.overlay_window,
            width=screen_width,
            height=screen_height,
            bg=bg_color,
            highlightthickness=0
        )
        self.overlay_canvas.pack()
        self.overlay_window.bind('<Escape>', self.close_overlay)
        self.overlay_canvas.bind('<Button-1>', self.check_click_location)
    
    def draw_bounding_boxes(self, qr_tuples) -> None:
        '''
        draws a bounding box overlay on screen for detected qr codes
        '''
        if not self.overlay_canvas:
            return
        
        for _, points_array in qr_tuples:
            # convert np array to flat list
            min_x = int(min(p[0] for p in points_array))
            max_x = int(max(p[0] for p in points_array))
            min_y = int(min(p[1] for p in points_array))
            max_y = int(max(p[1] for p in points_array))
            
            self.__create_rounded_rectangle(
                self.overlay_canvas,
                min_x, min_y, max_x, max_y,
                outline='lime',
                width=4,
                fill=''
            )
    
    def display_info(self, qr_tuples) -> None:
        '''
        displays decoded info near the bounding boxes for each qr code
        '''
        if not self.overlay_canvas:
            return
        
        for data, points_array in qr_tuples:
            if not data: continue 
            
            # display ... if too long
            display_text = (data[:47] + '...') if len(data) > 50 else data
            # bounding box coords
            min_x = int(min(p[0] for p in points_array))
            max_x = int(max(p[0] for p in points_array))
            min_y = int(min(p[1] for p in points_array))
            max_y = int(max(p[1] for p in points_array))
            
            info_frame = tk.Frame(self.overlay_canvas)
            label = tk.Label(info_frame, text=display_text)
            label.pack(side=tk.LEFT, padx=5, pady=5)
            
            # copy button
            copy_button = tk.Button(info_frame, image='', command=lambda d=data: self.copy_to_clipboard(d))
            copy_button.pack(side=tk.LEFT, padx=5, pady=5)
            
            # render to get size
            info_frame.update_idletasks()
            frame_width = info_frame.winfo_width()
            frame_height = info_frame.winfo_height()
            
            # info box position
            x = min_x
            y = max_y + 10
            
            self.overlay_canvas.create_window(int(x), int(y), window=info_frame, anchor='nw')

    def close_overlay(self, event=None) -> None:
        '''
        destroys the overlay window
        '''
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.destroy()
            self.overlay_window = None
            self.overlay_canvas = None
            print('Overlay closed')
    
    def check_click_location(self, event) -> None:
        '''
        checks if a click was on an empty area of the overlay
        closes the overlay if empty area
        '''
        items = self.overlay_canvas.find_overlapping(event.x, event.y, event.x, event.y)
        if not items: self.close_overlay()
    
    def copy_to_clipboard(self, text):
        '''
        copies string to clipboard
        '''
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        print(f'Copied to clipboard: {text}')

    def __create_rounded_rectangle(self, canvas, x1, y1, x2, y2, **kwargs) -> int:
        '''
        draws a rectangle with rounded corner on canvas
        '''
        radius = self.corner_radius
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
