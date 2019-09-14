import configparser
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
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
        self.size = tuple([int(x) for x in config['IMAGES']['SIZE'].split(',')])

        self.master.title("simplabel")
        self.img = self.it.get_image()

        menu = tk.Menu(master)
        master.config(menu=menu)

        sub_menu = tk.Menu(menu)
        menu.add_cascade(label="Options", menu=sub_menu)
        sub_menu.add_command(label='Images directory', command=self.select_dir)
        sub_menu.add_command(label='Edit classes', command=self.edit_classes)

        tk.Label(self.master, text="Annotator ID").pack(anchor=tk.W)
        tk.Entry(textvariable=self.e).pack(anchor=tk.W)
        tk.Label(self.master, text="Select the class that describes the image the best.").pack(anchor=tk.W)

        self.im_label = tk.Label(self.master, image=self.img)
        self.im_label.pack(anchor=tk.W)

        self.radio_buttons = []
        for i in range(len(self.classes)):
            self.radio_buttons.append(tk.Radiobutton(self.master,
                                                        text=self.classes[i],
                                                        variable=self.v,
                                                        value=self.classes[i]))
        for button in self.radio_buttons:
            button.pack(anchor=tk.W)

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

    def select_dir(self):
        try:
            self.master.withdraw()
            folder = filedialog.askdirectory()
            self.it = ImageTracker(folder, self.answers_file, self.size)
            new_img = self.it.get_image()
            self.im_label.configure(image=new_img)
            self.im_label.image = new_img
        except OSError:
            logging.error('Invaild directory!')
            messagebox.showerror('Error', 'Invaild directory!')
        except IndexError:
            logging.error("There is no images in the directory.")
            messagebox.showerror("Error", "Selected directory does not contain any images or all images have been annnotated.")
        except TypeError:
            logging.error('Directory not selected.')
            pass
        self.master.deiconify()

    def update_classes(self):
        for i in range(len(self.classes)):
            self.classes[i] = self.class_entry_values[i].get()
            self.radio_buttons[i].config(text=self.classes[i])

    def edit_classes(self):
        top = tk.Toplevel()
        top.title('Edit classes')
        self.class_entry_values = [tk.StringVar(top, value=class_name) for class_name in self.classes]
        for i in range(len(self.classes)):
            e = tk.Entry(master=top, textvariable=self.class_entry_values[i])
            e.pack(anchor=tk.W)
        tk.Button(top, text="Update", command=self.update_classes).pack(anchor=tk.W)
