import configparser
import logging
import tkinter as tk
from utils.image_tracker import ImageTracker
from utils.gui import SimplabelGUI

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('config.ini')

    IMAGES_DIR = config['DIRS']['IMAGES_DIR']
    ANSWERS_FILE = config['DIRS']['ANSWERS_FILE']
    IMAGE_SIZE = tuple([int(x) for x in config['IMAGES']['SIZE'].split(',')])

    master = tk.Tk()
    it = ImageTracker(IMAGES_DIR, ANSWERS_FILE, IMAGE_SIZE)
    gui = SimplabelGUI(master, it, config)
    tk.mainloop()