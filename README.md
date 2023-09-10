# README

## Image Annotation and Cropping Script

This Python script is designed to process a set of images and their corresponding YOLO8 annotation files and has been tested to work with Roboflow. It performs several tasks including:

1. Loading and displaying the original images and their annotations.
2. Padding the images to a specified size and drawing a checkerboard pattern on the padded area.
3. Cropping the padded images into smaller images of a specified size.
4. Adjusting the annotations to match the cropped images.
5. Saving the cropped images and their corresponding annotations to a specified output directory.

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