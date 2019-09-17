import configparser
import logging
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from utils.image_tracker import ImageTracker


class SimplabelGUI():
    def __init__(self, master, it, config):
        self.master = master
        self.config = config
        self.it = it

        self.classes = self.config['ANNOTATION']['CLASSES'].split(',')
        self.annotations_file = self.config['DIRS']['ANNOTATIONS_FILE']
        self.annotations_files = [os.path.join('data', x) for x in os.listdir('data')]
        self.selected_annotations_file = tk.StringVar()
        self.selected_annotations_file.set(self.annotations_files[0])
        self.size = tuple([int(x) for x in self.config['IMAGES']['SIZE'].split(',')])
        self.im_dir = self.config['DIRS']['IMAGES_DIR']
        self.is_im_dir_default = True

        if not os.path.exists(self.annotations_file):
            open(self.annotations_file, 'a').close()

        self.master.title("simplabel")
        self.master_top = tk.Frame(self.master)
        self.master_bottom = tk.Frame(self.master)
        self.master_top.pack(side=tk.TOP, anchor=tk.W)
        self.master_bottom.pack(side=tk.BOTTOM)

        self.img = self.it.get_image()

        self.v = tk.StringVar()
        self.e = tk.StringVar()

        menu = tk.Menu(master)
        master.config(menu=menu)

        sub_menu = tk.Menu(menu)
        menu.add_cascade(label="Options", menu=sub_menu)
        sub_menu.add_command(label='Images directory', command=self.select_dir)
        sub_menu.add_command(label='Edit classes', command=self.edit_classes)
        sub_menu.add_command(label='Change image preview size', command=self.change_im_size)
        sub_menu.add_command(label='Edit annotations file', command=self.edit_annotations)
        sub_menu.add_command(label='Show annotations', command=self.show_annotations)

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

    def refresh_image(self):
        self.it = ImageTracker(self.im_dir, self.annotations_file, self.size)
        new_img = self.it.get_image()
        self.im_label.configure(image=new_img)
        self.im_label.image = new_img

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
            with open(self.annotations_file, 'a') as f:
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
        self.size_popup.geometry("250x130")
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

    def create_annotations_file(self):
        if not self.new_annotations_entry.get():
            logging.error('Empty filename.')
            messagebox.showerror('Error', 'Filename cannot be empty!')
        else:
            new_annotations_file = 'data/' + self.new_annotations_entry.get() + '.csv'
            if not os.path.exists(new_annotations_file):
                open(new_annotations_file, 'a').close()
                self.annotations_files.append(new_annotations_file)
                self.file_select_menu.children['menu'].delete(0, "end")
                for file in self.annotations_files:
                    self.file_select_menu.children["menu"].add_command(label=file, command=lambda option=file: self.selected_annotations_file.set(file))
                self.selected_annotations_file.set(file)
                self.new_annotations_entry.config(textvariable=tk.StringVar())
            else:
                logging.error("File already exists.")
                messagebox.showerror("Error", "File already exists!")

    def remove_annotations_file(self):
        try:
            os.remove(self.selected_annotations_file.get())
            self.annotations_files.remove(self.selected_annotations_file.get())
            self.file_select_menu.children['menu'].delete(0, "end")
            for file in self.annotations_files:
                self.file_select_menu.children["menu"].add_command(label=file, command=lambda option=file: self.selected_annotations_file.set(file))
            if not self.annotations_files:
                self.selected_annotations_file.set('   ')
            else:
                self.selected_annotations_file.set(self.annotations_files[0])
        except FileNotFoundError:
            logging.error('File not found.')
            messagebox.showerror('Error', 'File not found!')

    def set_annotations_file(self):
        self.annotations_file = self.selected_annotations_file.get()

    def edit_annotations(self):
        annotations_popup = tk.Toplevel()
        annotations_popup.title('Edit annotations files')
        annotations_popup.geometry("300x240")

        tk.Label(annotations_popup, text='Enter filename (without extension).').pack(anchor=tk.W)
        v = tk.StringVar()
        self.new_annotations_entry = tk.Entry(master=annotations_popup, textvariable=v)
        self.new_annotations_entry.pack(anchor=tk.W)
        tk.Button(master=annotations_popup, text='Create file', command=self.create_annotations_file).pack(anchor=tk.W)

        tk.Label(annotations_popup, text='Select annotations file').pack(anchor=tk.W)
        self.file_select_menu = tk.OptionMenu(annotations_popup, self.selected_annotations_file, *self.annotations_files)
        self.file_select_menu.pack(anchor=tk.W)

        tk.Button(master=annotations_popup, text='Set as active', command=self.set_annotations_file).pack(anchor=tk.W)
        tk.Button(master=annotations_popup, text='Remove', command=self.remove_annotations_file).pack(anchor=tk.W)

    def refresh_file_preview(self):
        self.annotations_file_content.config(state=tk.NORMAL)
        self.annotations_file_content.delete('1.0', tk.END)
        with open(self.selected_annotations_file.get()) as f:
            self.annotations_file_content.insert(tk.END, f.read())
        self.annotations_file_content.config(state=tk.DISABLED)

    def show_annotations(self):
        annotations_content_popup = tk.Toplevel()
        annotations_content_popup.title('Annotations')
        annotations_content_popup_top = tk.Frame(annotations_content_popup)
        annotations_content_popup_bottom = tk.Frame(annotations_content_popup)
        annotations_content_popup_top.pack(side=tk.TOP, anchor=tk.W)
        annotations_content_popup_bottom.pack(side=tk.BOTTOM)

        tk.Label(master=annotations_content_popup, text='Select file').pack(in_=annotations_content_popup_top, side=tk.TOP)
        file_select_menu = tk.OptionMenu(annotations_content_popup, self.selected_annotations_file, *self.annotations_files)
        file_select_menu.pack(in_=annotations_content_popup_top, side=tk.LEFT)
        refresh_file_button = tk.Button(master=annotations_content_popup, text="Select", command=self.refresh_file_preview)
        refresh_file_button.pack(in_=annotations_content_popup_top, side=tk.LEFT)

        self.annotations_file_content = tk.Text(master=annotations_content_popup)
        self.annotations_file_content.pack(in_=annotations_content_popup_bottom, side=tk.TOP)
        self.refresh_file_preview()
