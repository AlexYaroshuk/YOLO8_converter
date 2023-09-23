# README

## Image Annotation and Cropping Script

This Python script is designed to process a set of images and their corresponding YOLO8 annotation files and has been tested to work with Roboflow. It performs several tasks including:

1. Loading and displaying the original images and their annotations.
2. Resizing the image to ensure it can be evenly split into 640 or 1280 px chunks. The script will check if the image can be split into 12 640px chunks. If it needs more than 12, the chunk size will double to reduce number of output images.
3. Adjusting the annotations to match the cropped images.
4. Saving the cropped images and their corresponding annotations to a specified output directory.
5. Saving resized images into a separate folder.

## Dependencies

The script uses several Python libraries including:

- `os`
- `sys`
- `PIL` (Pillow)
- `matplotlib`
- `shapely`
- `tqdm`

## Usage

Before running the script, you need to define the source classes of your images. These are the classes that your images are annotated with. For example:

The script also defines a set of global classes. These are the classes that the source classes will be translated to. If a source class is not in the list of global classes, it will be ignored.

The script then creates a mapping between the source classes and the global classes. This mapping is used to translate the class IDs in the annotation files.

The script also defines a set of colors for each class. These colors are used to display the annotations on the images.

The script then loads the images from a specified source folder and processes them one by one. For each image, it displays the original image and its annotations, pads the image, crops it into smaller images, adjusts the annotations to match the cropped images, and saves the cropped images and their annotations to a specified output directory.