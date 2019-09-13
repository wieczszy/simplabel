import os
import logging
from PIL import ImageTk, Image


class ImageTracker():
    def __init__(self, im_dir, answers_file, size):
        self.im_dir = im_dir
        self.answers_file = answers_file
        self.size = size
        self.index = 0
        self.imgs = []
        self._get_imgs()

    def _get_imgs(self):
        all_imgs = [os.path.join(self.im_dir, im) for im in os.listdir(self.im_dir)]
        all_imgs = [img for img in all_imgs if not os.path.isdir(img)]

        try:
            f = open(self.answers_file)
            done_imgs = [line.split(',')[1] for line in f]
            f.close()
        except FileNotFoundError:
            done_imgs = []
            
        final_imgs = [img for img in all_imgs if img not in done_imgs]

        if not final_imgs:
            logging.error('There is no images to annotate! Check if the directory is not empty.')
            exit()

        self.imgs = final_imgs

    def update_index(self):
        self.index += 1

    def get_image(self):
        im_pil = Image.open(self.imgs[self.index])
        im_pil = im_pil.resize(self.size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(im_pil)

    def get_filename(self):
        return self.imgs[self.index]