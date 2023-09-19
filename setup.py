from google.colab import files
import shutil
from PIL import Image, ImageDraw, ImageOps
import os

# Output folders for images and annotations
output_img_folder = 'output_images'
output_img_resized_folder = 'output_images_resized'
output_labels_folder = 'output_labels'
output_img_resizedto640_folder = 'output_images_resized640'

# Define the source folder
source_folder = 'source_images'
source_labels_folder = 'source_labels'

# Create output folders if they don't exist
os.makedirs(output_img_folder, exist_ok=True)
os.makedirs(output_labels_folder, exist_ok=True)
os.makedirs(source_folder, exist_ok=True)
os.makedirs(source_labels_folder, exist_ok=True)
os.makedirs(output_img_resized_folder, exist_ok=True)
os.makedirs(output_img_resizedto640_folder, exist_ok=True)

global_classes = [
    "AGRICULTURAL_OBJECT",
    "FIELD",
    "FOREST",
    "GRASSLAND",
    "INDUSTRIAL_FACILITY",
    "POWER_LINE",
    "PUBLIC_FACILITY",
    "RESIDENTIAL_FACILITY",
    "ROAD",
    "WATER",
    "NOT_MARKED_UP",
    "OTHER"
]
source_classes = []
source_class_map = {class_name: i for i,
                    class_name in enumerate(source_classes)}

used_classes = set()
class_ids = set()

global_class_map = {class_name: i for i,
                    class_name in enumerate(global_classes)}

# Create a dictionary to map source class values to global class values based on their indices
class_id_translation = {(i): source_classes[i]
                        for i in range(len(source_classes))}

# Print the translation
for source_class, global_class in class_id_translation.items():
    print(f"{source_class} => {global_class}")

# Define class colors for Matplotlib
class_colors_mpl = {
    'GRASSLAND': (0, 255, 0),
    'FOREST': (0, 127, 0),
    'ROAD': (127, 127, 127),
    'POWER_LINE': (255, 0, 255),
    'WATER': (0, 0, 255),
    'FIELD': (255, 255, 0),
    'INDUSTRIAL_FACILITY': (255, 0, 0),
    'RESIDENTIAL_FACILITY': (127, 0, 0),
    'PUBLIC_FACILITY': (0, 255, 255),
    'AGRICULTURAL_OBJECT': (127, 127, 0),
    'OTHER': (255, 255, 255),
    'NOT_MARKED_UP': (0, 0, 0)
}

class_colors_mpl_normalized = {
    global_class_map[class_name]: tuple(value / 255.0 for value in color)
    for class_name, color in class_colors_mpl.items()
}

input_crop_size = (640, 640)


def resize_and_count_chunks(image, input_crop_size):

    # Check if the original width or height is less than input_crop_size
    if width <= input_crop_size[0] or height <= input_crop_size[1]:
        return image, False, 0  # Return True when image is smaller than input_crop_size

    width_diff = width % input_crop_size[0]
    height_diff = height % input_crop_size[1]

    # Adjust the new dimensions to the closest multiples based on differences
    if width_diff <= input_crop_size[0] // 2:
        new_width = width - width_diff

    else:
        new_width = width + (input_crop_size[0] - width_diff)

    if height_diff <= input_crop_size[1] // 2:
        new_height = height - height_diff

    else:
        new_height = height + (input_crop_size[1] - height_diff)

    new_image = image.resize((new_width, new_height))

    # Calculate how many pieces of input_crop_size can fit in the width and height
    num_crop_width = new_width // input_crop_size[0]
    num_crop_height = new_height // input_crop_size[1]

    chunks_to_make = num_crop_width * num_crop_height

    # Check if both dimensions can fit at least 12 pieces of input_crop_size
    over_12_chunks = chunks_to_make > 12

    # If the number of chunks is 12 or more, set input_crop_size to (1280, 1280)
    if over_12_chunks:
        input_crop_size = (1280, 1280)

        width_diff = width % input_crop_size[0]
        height_diff = height % input_crop_size[1]

        # Adjust the new dimensions to the closest multiples based on differences
        if width_diff <= input_crop_size[0] // 2:
            new_width = width - width_diff

        else:
            new_width = width + (input_crop_size[0] - width_diff)

        if height_diff <= input_crop_size[1] // 2:
            new_height = height - height_diff

        else:
            new_height = height + (input_crop_size[1] - height_diff)

        new_image = image.resize((new_width, new_height))

    # Save the image to resized if it was resized

    if new_width != width or new_height != height:
        resized_image_path = os.path.join(
            output_img_resized_folder, f'{source_image}_resized.png')
        new_image.save(resized_image_path)
        print('Resized image saved to "output_images_resized"')

    return new_image, over_12_chunks, chunks_to_make


def resize_from_double(image):
    width, height = image.size
    new_width = width // 2
    new_height = height // 2
    resized_image = image.resize((new_width, new_height))
    return resized_image


# colored prints
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"

# draw plots if needed
draw_plots = False

# convert classes if needed
# Use data.yaml to create a conversion dict
translate_classes = True

source_classes = ['FOREST', 'GRASSLAND', 'ROAD', 'WATER']


def convert_number(number):
    conversion_dict = {
        0: 2,   # Replace with your conversion for number 0
        1: 3,   # Replace with your conversion for number 1
        2: 8,   # Replace with your conversion for number 2
        3: 9,   # Replace with your conversion for number 3

        # etc
    }

    if number in conversion_dict:
        return conversion_dict[number]
    else:
        return None  # Handle the case where the input number is not in the dictionary


# Example usage:
input_number = 3  # Replace with the number you want to convert
result = convert_number(input_number)
if result is not None:
    print(f"The converted number is: {result}")
else:
    print("Number not found in the conversion dictionary.")


# Download resized images


source_images = [f for f in os.listdir(source_folder) if f.endswith('.jpg')]

for source_image in source_images:

    original_image_path = os.path.join(source_folder, source_image)

    # Load the original image
    original_image = Image.open(original_image_path)

    resized640_image = original_image.resize((640, 640))

    resized640_image_path = os.path.join(
        output_img_resizedto640_folder, f'{source_image}_output_image_640.jpg')
    resized640_image.save(resized640_image_path)

# Download a folder archive


# Path to the output_img folder
output_img_folder = '/content/output_images'

# Create a ZIP archive of the output_img folder
shutil.make_archive(output_img_folder, 'zip', output_img_folder)

# Specify the ZIP file path
zip_file_path = f"{output_img_folder}.zip"

# Download the ZIP archive
files.download(zip_file_path)


# delete a folder
# Specify the path to the folder you want to delete
folder_path = '/content/output_labels'

shutil.rmtree(folder_path)
os.makedirs(folder_path, exist_ok=True)
folder_path = '/content/output_images'


shutil.rmtree(folder_path)
os.makedirs(folder_path, exist_ok=True)
folder_path = '/content/source_images'


shutil.rmtree(folder_path)
os.makedirs(folder_path, exist_ok=True)
folder_path = '/content/source_labels'


shutil.rmtree(folder_path)
os.makedirs(folder_path, exist_ok=True)
folder_path = '/content/output_images_resized'


shutil.rmtree(folder_path)
os.makedirs(folder_path, exist_ok=True)
