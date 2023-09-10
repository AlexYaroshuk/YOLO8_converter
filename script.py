import os
from PIL import Image, ImageDraw, ImageOps
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
import matplotlib.cm as cm
from matplotlib.patches import Patch
from shapely.geometry import MultiPolygon
from tqdm import tqdm
import sys

# Add this to another cell:
source_classes = ['FOREST', 'GRASSLAND', 'ROAD', 'WATER']

print("Initializing...")


print("Checking if source_classes is defined...")

if 'source_classes' not in globals():
    print("source_classes is not defined. Exiting the program.\n Запустите ячейку выше, чтобы задать исходные классы")
    sys.exit()

global_classes = [
    "NOT_MARKED_UP",
    "GRASSLAND",
    "FOREST",
    "ROAD",
    "POWER_LINE",
    "WATER",
    "FIELD",
    "INDUSTRIAL_FACILITY",
    "RESIDENTIAL_FACILITY",
    "PUBLIC_FACILITY",
    "AGRICULTURAL_OBJECT",
    "OTHER"
]

source_class_map = {class_name: i for i, class_name in enumerate(source_classes)}

used_classes = set()
class_ids = set()

global_class_map = {class_name: i for i, class_name in enumerate(source_classes)}

class_id_translation = {
    source_class_map[class_name]: global_class_map[class_name] for class_name in source_classes
}

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

# Normalize RGB values to the range [0, 1]
class_colors_mpl_normalized = {class_name: tuple(value / 255.0 for value in class_colors_mpl[class_name]) for class_name in global_classes}

class_id_to_name = {v: k for k, v in global_class_map.items()}

# Get a list of all the image files in the source folder
source_images = [f for f in os.listdir(source_folder) if f.endswith('.jpg')]

# Initialize progress bar for source images
pbar_images = tqdm(total=len(source_images), desc="Processing source images")

# Loop over all the image files
for source_image in source_images:

  # Define the paths to the image and its corresponding annotation file
  original_image_path = os.path.join(source_folder, source_image)
  original_annotation_path = os.path.join(source_labels_folder, source_image.replace('.jpg', '.txt'))

  # Load the original image
  original_image = Image.open(original_image_path)
  width, height = original_image.size

  # Create a figure and axis to display the image
  fig, ax = plt.subplots(1)
  ax.imshow(original_image)
  ax.set_title(f'Original Image {original_image.size}')

  print("Plotting original image & annotations...")

  # Load and display the original annotations as polygons
  with open(original_annotation_path, 'r') as annotation_file:
    for line in annotation_file:
        parts = line.strip().split()
        source_class_id = int(parts[0])
        source_class_name = class_id_to_name[source_class_id]

        # Translate the source class ID to the global class ID
        global_class_id = class_id_translation[source_class_id]

        # Replace the source class ID with the global class ID in the annotation
        parts[0] = str(global_class_id)

        used_classes.add(source_class_name)
        class_ids.add(target_class_id)
        vertices = [float(x) for x in parts[1:]]

        # Convert normalized coordinates to pixel coordinates
        pixel_vertices = [(int(vertices[i] * width), int(vertices[i + 1] * height)) for i in range(0, len(vertices), 2)]
        polygon = plt.Polygon(pixel_vertices, fill=False, edgecolor=class_colors_mpl_normalized[source_class_name], linewidth=1)

        # Add the polygon to the plot
        ax.add_patch(polygon)

  # Create a list of patches for the legend
  legend_patches = [Patch(color=color, label=class_name) for class_name, color in class_colors_mpl_normalized.items() if class_name in used_classes]
  ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

  # Show the image with annotations
  plt.show()

  # Desired size for the cropped images (250x250 for 4 output images)
  crop_size = (640, 640)

  # Calculate the padding needed to make the image size a multiple of the crop size
  pad_width = crop_size[0] - width % crop_size[0] if width % crop_size[0] != 0 else 0
  pad_height = crop_size[1] - height % crop_size[1] if height % crop_size[1] != 0 else 0

  # Create a new image with the padded size and a checkerboard pattern
  padded_image = Image.new('RGB', (width + pad_width, height + pad_height))

  # Create a draw object
  draw = ImageDraw.Draw(padded_image)

  # Define the size of the squares
  square_size = int(max(width, height) * 0.01)  # Adjust this value to change the size of the squares

  # Draw the checkerboard pattern
  for i in range(0, width + pad_width, square_size):
      for j in range(0, height + pad_height, square_size):
          if (i // square_size) % 2 == (j // square_size) % 2:
              draw.rectangle([i, j, i + square_size, j + square_size], fill='white')
          else:
              draw.rectangle([i, j, i + square_size, j + square_size], fill='gray')

  # Paste the original image onto the padded image
  padded_image.paste(original_image, (0, 0))

  # Replace the original image with the padded image
  original_image = padded_image

  # Store the original image dimensions
  original_width, original_height = width, height

  # Pad the original image
  original_image = ImageOps.expand(original_image, (0, 0, pad_width, pad_height))

  # Update the image size
  width, height = original_image.size

  # Calculate the scale factors for width and height
  scale_width = original_width / width
  scale_height = original_height / height

  # Calculate the number of rows and columns for cropping
  num_rows = height // crop_size[1]
  num_cols = width // crop_size[0]

  # Create a subplot grid
  fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 8))

  # Calculate total number of images
  total_images = num_rows * num_cols

  print("Calculating...")

  # Initialize progress bar
  pbar = tqdm(total=total_images, desc="Processing images")

  # Loop through each row and column to crop and save images
  for row in range(num_rows):
      for col in range(num_cols):

          # Calculate the cropping region
          left = int(col * crop_size[0])
          top = int(row * crop_size[1])
          right = int(left + crop_size[0])
          bottom = int(top + crop_size[1])

          # Calculate the region for the current cropped image
          region = (left / width, top / height, right / width, bottom / height)

          # Crop the image
          cropped_image = original_image.crop((left, top, right, bottom))

          # Save the cropped image
          output_image_path = os.path.join(output_img_folder, f'{source_image}_output_image_{row}_{col}.jpg')
          cropped_image.save(output_image_path)

          # Update progress bar
          pbar.update()


          # Load original annotations
          with open(original_annotation_path, 'r') as annotation_file:
              annotations = []
              for line in annotation_file:
                  parts = line.strip().split()
                  source_class_id = int(parts[0])
                  source_class_name = class_id_to_name[source_class_id]

                  # Translate the source class ID to the target class ID
                  target_class_id = class_id_translation[source_class_id]

                  # Replace the source class ID with the target class ID in the annotation
                  parts[0] = str(target_class_id)

                  # Parse normalized coordinates from the original annotation
                  coordinates = list(map(float, parts[1:]))

                  # Scale the coordinates of the polygons
                  scaled_coordinates = [(coordinates[i] * scale_width, coordinates[i + 1] * scale_height) for i in range(0, len(coordinates), 2)]

                  # Create a polygon from the vertices
                  polygon = Polygon(scaled_coordinates)

                  # Create a box representing the boundary of the cropped region
                  boundary = box(region[0], region[1], region[2], region[3])

                  # Clip the polygon to the boundary
                  clipped_polygon = polygon.intersection(boundary)

                  # Check if the clipped polygon is not empty
                  if not clipped_polygon.is_empty:

                      # Check if the clipped polygon is a MultiPolygon
                      if isinstance(clipped_polygon, MultiPolygon):

                        # Handle each Polygon in the MultiPolygon separately
                        for poly in clipped_polygon.geoms:

                            # Convert the clipped polygon to a list of vertices
                            clipped_vertices = list(poly.exterior.coords)


                            # Translate normalized coordinates to cropped image coordinates
                            clipped_vertices = [((x - left) / crop_size[0], (y - top) / crop_size[1]) for x, y in clipped_vertices]

                            # Append the annotation to the list for this cropped image
                            annotations.append(
                                f'{class_label} ' + ' '.join(map(str, [coord for vertex in clipped_vertices for coord in vertex]))
                            )
                      else:

                          # Convert the clipped polygon to a list of vertices
                          if isinstance(clipped_polygon, Polygon):
                            clipped_vertices = list(clipped_polygon.exterior.coords)

                          # Translate normalized coordinates to cropped image coordinates
                          clipped_vertices = [((x - region[0]) / (region[2] - region[0]), (y - region[1]) / (region[3] - region[1])) for x, y in clipped_vertices]

                          # Append the annotation to the list for this cropped image
                          annotations.append(
                              f'{target_class_id} ' + ' '.join(map(str, [coord for vertex in clipped_vertices for coord in vertex]))
                          )

              # Create a draw object
              draw = ImageDraw.Draw(cropped_image)

              # Loop through annotations for the current output image
              for annotation in annotations:
                  parts = annotation.split()

                  # Get the class label
                  class_label = parts[0]


                  # Parse normalized coordinates from the annotation
                  coordinates = list(map(float, parts[1:]))
                  vertices = []
                  for i in range(0, len(coordinates), 2):
                        x = coordinates[i] * crop_size[0]
                        y = coordinates[i + 1] * crop_size[1]

                        # Adjust positions via shift values if needed

                        ''' # Calculate the shift value
                        shift_value_x = 0 if pad_width == 0 or x == crop_size[0] else 0.01 * pad_width + 0.02 * (x + ((col)* crop_size[0]))
                        shift_value_y = 0 if pad_height == 0 or y == crop_size[1] else  0.02 * (y + ((row)* crop_size[1]))

                        print(f"pw: {pad_width}, ph: {pad_height} w:{width} col: {col}, sX: {shift_value_x}, sY: {shift_value_y}, x:{x}, y:{y}") '''

                        shift_value_x = 0
                        shift_value_y = 0
                        vertices.append((x - shift_value_x, y - shift_value_y))  # Adjust the x-coordinate of the vertex

                  # Draw the polygon with the color corresponding to the class
                  draw.polygon(vertices, outline=class_colors_mpl[class_id_to_name[int(class_label)]], width=8)

              # Display the cropped image with annotations
              fig.suptitle(f'Output images @ {crop_size[0]} x {crop_size[1]}')
              if num_rows == 1:
                  if num_cols == 1:
                      axs.imshow(cropped_image)
                      axs.set_title(f'Output Image {row}_{col}')
                      axs.set_aspect('equal')  # Set aspect ratio to be equal
                  else:
                      axs[col].imshow(cropped_image)
                      axs[col].set_title(f'Output Image {row}_{col}')
                      axs[col].set_aspect('equal')  # Set aspect ratio to be equal
              elif num_cols == 1:
                  axs[row].imshow(cropped_image)
                  axs[row].set_title(f'Output Image {row}_{col}')
                  axs[row].set_aspect('equal')  # Set aspect ratio to be equal
              else:
                  axs[row, col].imshow(cropped_image)
                  axs[row, col].set_title(f'Output Image {row}_{col}')
                  axs[row, col].set_aspect('equal')  # Set aspect ratio to be equal

          # Save annotations to a file with the same name as the image
          output_annotation_path = os.path.join(output_labels_folder, f'{source_image}_output_image_{row}_{col}.txt')
          with open(output_annotation_path, 'w') as annotation_output_file:
              for annotation in annotations:
                  annotation_output_file.write(annotation + '\n')
  pbar_images.update()

  # Close progress bar
  pbar.close()

  # Remove empty subplots (if the number of images is not a multiple of images_per_row)
  for i in range(num_rows * num_cols, num_rows):
      axs[i].axis('off')

  print("Drawing plots...")
  fig.legend(handles=legend_patches, loc='upper right')
  plt.tight_layout()
  plt.show()





with open('class_map.txt', 'w') as f:
    for class_name in classes:
        f.write(f'{class_name}\n')


# Close progress bar for source images
pbar_images.close()
print("Images & labels ready, run the cells below to download ZIP")
print("Make sure to also download class_map.txt and upload it with the dataset")