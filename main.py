from qr_scanner import QRScanner 
from ui import UI

import tkinter as tk

def main():
    scanner = QRScanner()
    root = tk.Tk()
    app = UI(root, scanner)
    root.mainloop()
    
if __name__=="__main__":
    main()
