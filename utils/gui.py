import configparser
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from utils.image_tracker import ImageTracker


class SimplabelGUI():
    def __init__(self, master, it, config):
        self.master = master
        self.master_top = tk.Frame(self.master)
        self.master_bottom = tk.Frame(self.master)
        self.master_top.pack(side=tk.TOP, anchor=tk.W)
        self.master_bottom.pack(side=tk.BOTTOM)
        self.config = config
        self.it = it
        self.v = tk.StringVar()
        self.e = tk.StringVar()
        self.classes = self.config['ANNOTATION']['CLASSES'].split(',')
        self.answers_file = self.config['DIRS']['ANSWERS_FILE']
        self.size = tuple([int(x) for x in self.config['IMAGES']['SIZE'].split(',')])
        self.im_dir = self.config['DIRS']['IMAGES_DIR']
        self.is_im_dir_default = True

        self.master.title("simplabel")
        self.img = self.it.get_image()

        menu = tk.Menu(master)
        master.config(menu=menu)

        sub_menu = tk.Menu(menu)
        menu.add_cascade(label="Options", menu=sub_menu)
        sub_menu.add_command(label='Images directory', command=self.select_dir)
        sub_menu.add_command(label='Edit classes', command=self.edit_classes)
        sub_menu.add_command(label='Change image size', command=self.change_im_size)

        tk.Label(self.master, text="Annotator ID:").pack(in_=self.master_top, side=tk.LEFT)
        tk.Entry(textvariable=self.e).pack(in_=self.master_top, side=tk.LEFT)
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

        tk.Button(self.master, text="Submit", command=self.callback).pack(in_=self.master_bottom, side=tk.LEFT)
        tk.Button(self.master, text="Exit", command=self.close_window).pack(in_=self.master_bottom, side=tk.LEFT)

    def callback(self):
        if self.is_im_dir_default:
            logging.error("Images directory has not been selected.")
            messagebox.showerror("Error", "Images directory has not been selected!")
        elif not self.classes:
            logging.error("There are no classes!")
            messagebox.showerror("Error", "There are no classes to use!")
        elif not self.e.get():
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
                self.im_dir = self.config['DIRS']['IMAGES_DIR']
                self.is_im_dir_default = True
                self.refresh_image()

    def close_window(self):
        self.master.destroy()

    def select_dir(self):
        tmp = self.im_dir
        try:
            self.master.withdraw()
            self.im_dir = filedialog.askdirectory()
            self.refresh_image()
            if not self.im_dir == tmp:
                self.is_im_dir_default = False
        except OSError:
            logging.error('Invaild directory!')
            messagebox.showerror('Error', 'Invaild directory!')
        except IndexError:
            logging.error("There is no images in the directory.")
            messagebox.showerror("Error", "Selected directory does not contain any images or all images have been annnotated.")
            self.im_dir = self.config['DIRS']['IMAGES_DIR']
            self.is_im_dir_default = True
            self.refresh_image()
        except TypeError:
            logging.error('Directory not selected.')
            pass
        self.master.deiconify()

    def edit_classes(self):
        self.classes_popup = tk.Toplevel()
        self.classes_popup_top = tk.Frame(self.classes_popup)
        self.classes_popup_bottom = tk.Frame(self.classes_popup)
        self.classes_popup_top.pack(side=tk.TOP)
        self.classes_popup_bottom.pack(side=tk.BOTTOM)
        self.classes_popup.title('Edit classes')
        u = tk.Button(self.classes_popup, text="Update", command=self.update_classes)
        a = tk.Button(self.classes_popup, text="Add class", command=self.add_class)
        r = tk.Button(self.classes_popup, text="Remove class", command=self.remove_class)
        u.pack(in_=self.classes_popup_top, side=tk.LEFT)
        a.pack(in_=self.classes_popup_top, side=tk.LEFT)
        r.pack(in_=self.classes_popup_top, side=tk.LEFT)
        self.class_entry_values = [tk.StringVar(self.classes_popup, value=class_name) for class_name in self.classes]
        self.edit_class_entries = []
        for i in range(len(self.classes)):
            e = tk.Entry(master=self.classes_popup, textvariable=self.class_entry_values[i])
            e.pack(in_=self.classes_popup_bottom, anchor=tk.W)
            self.edit_class_entries.append(e)

    def update_classes(self):
        for i in range(len(self.classes)):
            self.classes[i] = self.class_entry_values[i].get()
            self.radio_buttons[i].config(text=self.classes[i])

    def add_class(self):
        v = tk.StringVar(value="New class")
        e = tk.Entry(master=self.classes_popup_bottom, textvariable=v)
        e.pack(anchor=tk.SW)
        self.classes.append(e.get())
        self.edit_class_entries.append(e)
        self.class_entry_values.append(e)
        b = tk.Radiobutton(self.master, text=self.classes[-1], variable=self.v, value=self.classes[-1])
        b.pack(anchor=tk.W)
        self.radio_buttons.append(b)

    def remove_class(self):
        try:
            self.edit_class_entries[-1].pack_forget()
            self.radio_buttons[-1].pack_forget()
            del self.edit_class_entries[-1]
            del self.class_entry_values[-1]
            del self.classes[-1]
            del self.radio_buttons[-1]
        except IndexError:
            logging.error('There are no classes to remove.')
            messagebox.showerror('Error', 'There are no classes to remove!')

    def change_im_size(self):
        self.size_popup = tk.Toplevel()
        self.size_popup.title('Image preview size')
        self.size_popup.geometry("250x150")
        w = tk.StringVar()
        h = tk.StringVar()
        tk.Label(self.size_popup, text='Width').pack(anchor=tk.W)
        self.new_width = tk.Entry(self.size_popup, textvariable=w)
        self.new_width.pack(anchor=tk.W)
        tk.Label(self.size_popup, text='Heigth').pack(anchor=tk.W)
        self.new_height = tk.Entry(self.size_popup, textvariable=h)
        self.new_height.pack(anchor=tk.W)
        tk.Button(self.size_popup, text='Submit', command=self.update_im_size).pack(anchor=tk.W)

    def update_im_size(self):
        try:
            self.size = (int(self.new_width.get()), int(self.new_height.get()))
            self.refresh_image()
        except ValueError:
            logging.error('Invalid image size.')
            messagebox.showerror('Error', 'Set valid image size!')

    def refresh_image(self):
        self.it = ImageTracker(self.im_dir, self.answers_file, self.size)
        new_img = self.it.get_image()
        self.im_label.configure(image=new_img)
        self.im_label.image = new_img