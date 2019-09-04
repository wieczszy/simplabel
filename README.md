# simplabel
Simple tool that lets you assign images to classes of your choice. Results are saved in a CSV file. Hacked together for my own use so may not work the best. Built with `tkinter`, `pillow` and `Python 3.6.8`.  

![example](https://i.imgur.com/T8Ff69j.png)

## Usage
Set directories, classes and size of the image in the preview according to your needs in `config.ini`. Example:
```
[DIRS]
images_dir = data/images
answers_file = data/answers.csv

[ANNOTATION]
classes = amusement, anger, awe, contentment, disgust, excitement, fear, sadness

[IMAGES]
size = 500,500
```
Then run the app with `python app.py`. Annotations are saved in the file specified in the config. When starting, the app checks whether the image have been already annotated so you don't have to annotate all images at once as long as you keep the same results file. Example files are provided in the repo. 
