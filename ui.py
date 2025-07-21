from screeninfo import get_monitors

import tkinter as tk


class UI:
    def __init__(self, root, qr_scanner):
        self.root = root
        self.scanner = qr_scanner
        self.overlay_window = None
        self.overlay_canvas = None
        self.root.title('QR Code Scanner')
        self.root.geometry('500x200')
        
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
    
    def scan_and_display(self, event=None):
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
            points_list = [int(coord) for point in points_array for coord in point]
            self.overlay_canvas.create_polygon(
                points_list,
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
            
            # position text above top left
            x = int(min(p[0] for p in points_array))
            y = int(min(p[1] for p in points_array)) - 25 

            # background
            text_id = self.overlay_canvas.create_text(
                x, y,
                text=data,
                fill='white',
                anchor='nw'
            )
            bbox = self.overlay_canvas.bbox(text_id)
            rect_id = self.overlay_canvas.create_rectangle(
                bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5,
                fill='black',
                outline='black'
            )
            self.overlay_canvas.tag_raise(text_id, rect_id)

    def close_overlay(self, event=None):
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
    
