import configparser
import json
import os
import logging
import tkinter as tk
from utils.image_tracker import ImageTracker


def callback():
    if not e.get():
        tk.messagebox.showerror("Error", "Enter your ID!")
    elif not v.get():
        tk.messagebox.showerror("Error", "Select one option!")
    else:
        print('{},{},{}'.format(e.get(), it.get_filename(), v.get()))
        with open(ANSWERS_FILE, 'a') as f:
            f.write('{},{},{}\n'.format(e.get(), it.get_filename(), v.get()))
        try:
            it.update_index()
            new_img = it.get_image()
            im_label.configure(image=new_img)
            im_label.image = new_img
        except IndexError:
            logging.info("There is no more images to annotate")
            tk.messagebox.showinfo("You're done!", "The is no more images")
            exit()

def close_window(): 
    master.destroy()

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('config.ini')

    IMAGES_DIR = config['DIRS']['IMAGES_DIR']
    ANSWERS_FILE = config['DIRS']['ANSWERS_FILE']
    CLASSES = config['ANNOTATION']['CLASSES'].split(',')
    IMAGE_SIZE = tuple([int(x) for x in config['IMAGES']['SIZE'].split(',')])

    master = tk.Tk()
    master.title("Image annotation tool")

    v = tk.StringVar()
    e = tk.StringVar()

    it = ImageTracker(IMAGES_DIR, ANSWERS_FILE, IMAGE_SIZE)
    img = it.get_image()

    tk.Label(master, text="Annotator ID").pack(anchor=tk.W)
    tk.Entry(textvariable=e).pack(anchor=tk.W)
    tk.Label(master, text="Select the class that describes the image the best.").pack(anchor=tk.W)

    im_label = tk.Label(master, image=img)
    im_label.pack(anchor=tk.W)

    for i in range(len(CLASSES)):
        tk.Radiobutton(master, text=CLASSES[i], variable=v, value=CLASSES[i]).pack(anchor=tk.W)

    tk.Button(master, text="Submit", command=callback).pack(anchor=tk.W)
    tk.Button(master, text="Exit", command=close_window).pack(anchor=tk.W)

    tk.mainloop()
