import os
import tkinter as tk
from utils import src_path
from poggendorff_checker import PoggendorffChecker

def main():
    win = tk.Tk()
    win.iconbitmap(src_path(".\\src\\img\\icon.ico"))
    
    app = PoggendorffChecker(master=win, font_path = src_path('.\\src\\font\\font.ttf'))
    app.run()

if __name__ == '__main__':
    main()