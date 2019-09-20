# simplabel
Simple tool that lets you assign images to classes of your choice. Results are saved in a CSV file. Hacked together for my own use so may not work the best. Built with `tkinter`, `pillow` and `Python 3.6.8`.  

![example](https://i.imgur.com/TXBP4dc.png)

## Usage
Install requirements (it's `PIL` only, the rest should come by default with Python): `pip install -r requirements.txt`.

Then run the app with `python app.py`. When starting, the app checks whether the image have been already annotated so you don't have to annotate all images at once as long as you keep the same results file.

Selecting images' directory, changing classes and other options are available in the menu.

## tkinter error
If you get the error: `ImportError: No module named 'tkinter'` on Linux then try:

`sudo apt-get install python3-tk`

On Windows `tkinter` should come by default when installing Python. 
