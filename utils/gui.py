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

        if os.name == 'nt':
            self.master.state('zoomed')
        else:
            self.master.attributes('-zoomed', True)

        self.classes = self.config['ANNOTATION']['CLASSES'].split(',')
        self.default_annotations_file = self.config['DIRS']['ANNOTATIONS_FILE']
        self.annotations_files = [os.path.join('data', x) for x in os.listdir('data')]
        self.active_annotations_file = tk.StringVar()
        self.annotator_id_entry_state = 1

        if not self.annotations_files:
            open(self.default_annotations_file, 'a').close()
            self.annotations_files.append(self.default_annotations_file)

        self.active_annotations_file.set(self.annotations_files[0])
        self.size = tuple([int(x) for x in self.config['IMAGES']['SIZE'].split(',')])
        self.im_dir = self.config['DIRS']['IMAGES_DIR']
        self.is_im_dir_default = True

        self.master.title("simplabel")
        self.master_top = tk.Frame(self.master)
        self.master_bottom = tk.Frame(self.master)
        self.master_top.pack(side=tk.TOP, anchor=tk.W)
        self.master_bottom.pack(side=tk.BOTTOM)

        self.resize = tk.BooleanVar()
        self.resize.set(False)

        self.img = self.it.get_image(self.resize.get())

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
        self.annotator_id_entry = tk.Entry(textvariable=self.e)
        self.annotator_id_entry.pack(in_=self.master_top, side=tk.LEFT)
        self.annotator_id_button = tk.Button(self.master, text="Set ID", command=self.toggle_entry_state)
        self.annotator_id_button.pack(in_=self.master_top, side=tk.LEFT)
        tk.Label(self.master, text="Select classes according to your task description.").pack(anchor=tk.W)

        self.im_label = tk.Label(self.master, image=self.img)
        self.im_label.pack(anchor=tk.W)

        self.radio_buttons = []
        for i in range(len(self.classes)):
            button_label = f'[{i+1}] {self.classes[i]}'
            self.radio_buttons.append(tk.Radiobutton(self.master,
                                                        text=button_label,
                                                        variable=self.v,
                                                        value=self.classes[i]))
        for button in self.radio_buttons:
            button.pack(anchor=tk.W)

        tk.Button(self.master, text="Submit", command=self.submit_annotation).pack(in_=self.master_bottom, side=tk.LEFT)
        tk.Button(self.master, text="Exit", command=self.close_window).pack(in_=self.master_bottom, side=tk.LEFT)

        for i in range(1, len(self.classes) + 1):
            self.master.bind(f"{i}", lambda i: self.annotate_by_key(i))

    def annotate_by_key(self, i):
        if self.annotator_id_entry_state:
            # messagebox.showerror("Error", "Set Annotator ID to use key-shortcuts.")
            pass
        else:
            self.v.set(self.classes[int(i.char) - 1])
            self.submit_annotation()

    def toggle_entry_state(self):
        if self.annotator_id_entry_state:
            self.annotator_id_entry.config(state=tk.DISABLED)
            self.annotator_id_entry_state = 0
            self.annotator_id_button.config(text="Change ID")
        else:
            self.annotator_id_entry.config(state=tk.NORMAL)
            self.annotator_id_entry_state = 1
            self.annotator_id_button.config(text="Set ID")

    def refresh_image(self):
        self.it = ImageTracker(self.im_dir, self.active_annotations_file.get(), self.size)
        new_img = self.it.get_image(self.resize.get())
        self.im_label.configure(image=new_img)
        self.im_label.image = new_img

    def submit_annotation(self):
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
            with open(self.active_annotations_file.get(), 'a') as f:
                f.write('{},{},{}\n'.format(self.e.get(), self.it.get_filename(), self.v.get()))
            try:
                self.it.update_index()
                new_img = self.it.get_image(self.resize.get())
                self.im_label.configure(image=new_img)
                self.im_label.image = new_img
            except IndexError:
                logging.error("All images have been annotated.")
                messagebox.showinfo("You're done!", "All images have been annotated!.")
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
        classes_popup = tk.Toplevel()
        classes_popup.attributes('-topmost', True)
        classes_popup_top = tk.Frame(classes_popup)
        self.classes_popup_bottom = tk.Frame(classes_popup)
        classes_popup_top.pack(side=tk.TOP)
        self.classes_popup_bottom.pack(side=tk.BOTTOM)
        classes_popup.title('Edit classes')

        u = tk.Button(classes_popup, text="Update", command=self.update_classes)
        a = tk.Button(classes_popup, text="Add class", command=self.add_class)
        r = tk.Button(classes_popup, text="Remove class", command=self.remove_class)
        u.pack(in_=classes_popup_top, side=tk.LEFT)
        a.pack(in_=classes_popup_top, side=tk.LEFT)
        r.pack(in_=classes_popup_top, side=tk.LEFT)

        self.class_entry_values = [tk.StringVar(classes_popup, value=class_name) for class_name in self.classes]
        self.edit_class_entries = []

        for i in range(len(self.classes)):
            e = tk.Entry(master=classes_popup, textvariable=self.class_entry_values[i])
            e.pack(in_=self.classes_popup_bottom, anchor=tk.W)
            self.edit_class_entries.append(e)

    def update_classes(self):
        for i in range(len(self.classes)):
            self.classes[i] = self.class_entry_values[i].get()
            button_label = f'[{i+1}] {self.classes[i]}'
            self.radio_buttons[i].config(text=button_label, value=self.classes[i])
        for i in range(1, len(self.classes) + 1):
            self.master.bind(f"{i}", lambda i: self.annotate_by_key(i))
        if len(self.classes) > 9:
            messagebox.showinfo("Key shortcuts", "Remember that only 9 classes are supported by key shortcuts. You can still use radiobuttons for the rest.")

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
        size_popup = tk.Toplevel()
        size_popup.attributes('-topmost', True)
        size_popup.title('Image preview size')
        size_popup.geometry("250x180")
        w = tk.StringVar()
        h = tk.StringVar()
        tk.Checkbutton(size_popup, text='Resize images', variable=self.resize, onvalue=True, offvalue=False).pack(anchor=tk.W)
        tk.Label(size_popup, text='Width').pack(anchor=tk.W)
        self.new_width = tk.Entry(size_popup, textvariable=w)
        self.new_width.pack(anchor=tk.W)
        tk.Label(size_popup, text='Heigth').pack(anchor=tk.W)
        self.new_height = tk.Entry(size_popup, textvariable=h)
        self.new_height.pack(anchor=tk.W)
        tk.Button(size_popup, text='Submit', command=self.update_im_size).pack(anchor=tk.W)
        tk.Button(size_popup, text='Reset', command=self.reset_resizing).pack(anchor=tk.W)

    def update_im_size(self):
        if self.resize.get():
            try:
                self.size = (int(self.new_width.get()), int(self.new_height.get()))
                self.refresh_image()
            except ValueError:
                logging.error('Invalid image size.')
                messagebox.showerror('Error', 'Set valid image size!')
        else:
            messagebox.showinfo('Resizing disabled', 'Enable resizing if you want to apply changes.')

    def reset_resizing(self):
        self.resize.set(False)
        self.refresh_image()

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
                    self.file_select_menu.children["menu"].add_command(label=file, command=lambda option=file: self.active_annotations_file.set(option))
                self.active_annotations_file.set(file)
                self.new_annotations_entry.config(textvariable=tk.StringVar())
            else:
                logging.error("File already exists.")
                messagebox.showerror("Error", "File already exists!")

    def remove_annotations_file(self):
        try:
            os.remove(self.active_annotations_file.get())
            self.annotations_files.remove(self.active_annotations_file.get())
            self.file_select_menu.children['menu'].delete(0, "end")
            for file in self.annotations_files:
                self.file_select_menu.children["menu"].add_command(label=file, command=lambda option=file: self.active_annotations_file.set(option))
            if not self.annotations_files:
                self.active_annotations_file.set('   ')
            else:
                self.active_annotations_file.set(self.annotations_files[0])
        except FileNotFoundError:
            logging.error('File not found.')
            messagebox.showerror('Error', 'File not found!')

    def edit_annotations(self):
        popup_window = tk.Toplevel()
        popup_window.attributes('-topmost', True)
        popup_window.title('Edit annotations files')
        popup_window.geometry("300x180")

        popup_window_top = tk.Frame(popup_window)
        popup_window_bottom = tk.Frame(popup_window)
        popup_window_top.pack(anchor=tk.W)
        popup_window_bottom.pack(anchor=tk.W)

        popup_window_bottom_top = tk.Frame(popup_window_bottom)
        popup_window_bottom_bottom = tk.Frame(popup_window_bottom)
        popup_window_bottom_top.pack(anchor=tk.W)
        popup_window_bottom_bottom.pack(anchor=tk.W)

        tk.Label(popup_window, text='Enter filename (without extension).').pack(in_=popup_window_top, anchor=tk.W)
        v = tk.StringVar()
        self.new_annotations_entry = tk.Entry(master=popup_window, textvariable=v)
        self.new_annotations_entry.config(width=300)
        self.new_annotations_entry.pack(in_=popup_window_top, anchor=tk.W)
        tk.Button(master=popup_window, text='Create file', command=self.create_annotations_file).pack(in_=popup_window_top, side=tk.LEFT)

        tk.Label(popup_window, text='Select annotations file to use').pack(in_=popup_window_bottom_top, anchor=tk.W)
        self.file_select_menu = tk.OptionMenu(popup_window, self.active_annotations_file, *self.annotations_files)
        self.file_select_menu.config(width=300)
        self.file_select_menu.pack(in_=popup_window_bottom_top, side=tk.LEFT)

        tk.Button(master=popup_window, text='Remove', command=self.remove_annotations_file).pack(in_=popup_window_bottom_bottom, side=tk.RIGHT)

    def refresh_file_preview(self):
        self.annotations_file_content.config(state=tk.NORMAL)
        self.annotations_file_content.delete('1.0', tk.END)
        with open(self.annotations_file_to_preview.get()) as f:
            self.annotations_file_content.insert(tk.END, f.read())
        self.annotations_file_content.config(state=tk.DISABLED)

    def show_annotations(self):
        popup_window = tk.Toplevel()
        popup_window.attributes('-topmost', True)
        popup_window.title('Annotations')
        popupwindow_top = tk.Frame(popup_window)
        popup_window_bottom = tk.Frame(popup_window)
        popupwindow_top.pack(side=tk.TOP, anchor=tk.W)
        popup_window_bottom.pack(side=tk.TOP)

        tk.Label(master=popup_window, text='Select file').pack(in_=popupwindow_top, side=tk.TOP)
        self.annotations_file_to_preview = tk.StringVar()
        self.annotations_file_to_preview.set(self.active_annotations_file.get())
        annotations_select_menu = tk.OptionMenu(popup_window, self.annotations_file_to_preview, *self.annotations_files)
        annotations_select_menu.pack(in_=popupwindow_top, side=tk.LEFT)
        refresh_file_button = tk.Button(master=popup_window, text="Select", command=self.refresh_file_preview)
        refresh_file_button.pack(in_=popupwindow_top, side=tk.LEFT)

        x_scrollbar = tk.Scrollbar(master=popup_window, orient=tk.HORIZONTAL, bg='#4C565E')
        y_scrollbar = tk.Scrollbar(master=popup_window, orient=tk.VERTICAL, bg='#4C565E')
        self.annotations_file_content = tk.Text(master=popup_window, wrap=tk.NONE, xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        x_scrollbar.config(command=self.annotations_file_content.xview)
        y_scrollbar.config(command=self.annotations_file_content.yview)
        x_scrollbar.pack(in_=popup_window_bottom, side=tk.BOTTOM, fill=tk.X)
        y_scrollbar.pack(in_=popup_window_bottom, side=tk.RIGHT, fill=tk.Y)
        self.annotations_file_content.pack(in_=popup_window_bottom, side=tk.TOP, fill=tk.BOTH, expand=True)
        self.refresh_file_preview()
