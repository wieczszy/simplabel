import configparser
import logging
import tkinter as tk
from tkinter import messagebox
from utils.image_tracker import ImageTracker


class SimplabelGUI():
    def __init__(self, master, it, config):
        self.master = master
        self.config = config
        self.it = it
        self.v = tk.StringVar()
        self.e = tk.StringVar()
        self.classes = config['ANNOTATION']['CLASSES'].split(',')
        self.answers_file = config['DIRS']['ANSWERS_FILE']

        self.master.title("Image annotation tool")
        self.img = self.it.get_image()

        tk.Label(self.master, text="Annotator ID").pack(anchor=tk.W)
        tk.Entry(textvariable=self.e).pack(anchor=tk.W)
        tk.Label(self.master, text="Select the class that describes the image the best.").pack(anchor=tk.W)

        self.im_label = tk.Label(self.master, image=self.img)
        self.im_label.pack(anchor=tk.W)

        for i in range(len(self.classes)):
            tk.Radiobutton(self.master, 
                           text=self.classes[i], 
                           variable=self.v, 
                           value=self.classes[i]).pack(anchor=tk.W)

        tk.Button(self.master, text="Submit", command=self.callback).pack(anchor=tk.W)
        tk.Button(self.master, text="Exit", command=self.close_window).pack(anchor=tk.W)

    def callback(self):
        if not self.e.get():
            logging.error("Annotator ID has not been entered.")
            messagebox.showerror("Error", "Enter your ID!")
        elif not self.v.get():
            logging.error("Class has not been selected.")
            messagebox.showerror("Error", "Select class!")
        else:
            print('{},{},{}'.format(self.e.get(), self.it.get_filename(), self.v.get()))
            with open(self.answers_file, 'a') as f:
                f.write('{},{},{}\n'.format(self.e.get(), self.it.get_filename(), self.v.get()))
            try:
                self.it.update_index()
                new_img = self.it.get_image()
                self.im_label.configure(image=new_img)
                self.im_label.image = new_img
            except IndexError:
                logging.error("There is no more images to annotate.")
                messagebox.showinfo("You're done!", "The is no more images.")
                exit()

    def close_window(self): 
        self.master.destroy()
