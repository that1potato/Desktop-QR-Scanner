from qr_scanner import QRScanner 
from ui import UI
from pynput import keyboard

import tkinter as tk


def main():
    scanner = QRScanner()
    root = tk.Tk()
    app = UI(root, scanner)
    
    def on_activate():
        '''
        schedules the scan to run on the main tkinter thread
        '''
        root.after(0, app.scan_and_display)
    
    def on_press(key):
        if key == keyboard.Key.esc:
            root.after(0, app.close_overlay)
        hotkey.press(listener.canonical(key))

    def on_release(key):
        hotkey.release(listener.canonical(key))

    # global scanning
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<cmd>+<shift>+1'),
        on_activate
    )

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    
    listener.start()
    root.mainloop()
    
if __name__=="__main__":
    main()
