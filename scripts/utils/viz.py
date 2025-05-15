import os
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

def load_and_display_page_level(jsonfolder, imagefolder, uuid, MAX_WIDTH, MAX_HEIGHT, FULL_WIDTH_RECTANGLES,SAVE=False):
    """
    Loads an image and its corresponding JSON annotations, then displays it with bounding boxes
    and text in a right margin aligned with the centroid of each detected object.
    """
    # Load JSON file
    path = os.path.join(jsonfolder, uuid + '.json')
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    
    print(f'Number of lines in image: {len(data["objects"])}')

    # Open the corresponding image
    image_path = os.path.join(imagefolder, uuid + '.jpg')  # Fixed variable name
    image = Image.open(image_path)

    # Get original image size
    original_width, original_height = image.size

    # Compute scaling factor (since aspect ratio was preserved)
    scaling_factor = min(1.0, MAX_WIDTH / original_width, MAX_HEIGHT / original_height)

    # Compute the width and height of the image used in JSON
    json_width = int(original_width * scaling_factor)
    json_height = int(original_height * scaling_factor)

    # Resize image for display (maintaining aspect ratio)
    display_width = 700  # Adjust as needed
    display_height = int(display_width * (original_height / original_width))

    # Define right margin width
    margin_width = 500  # Increased margin for larger text
    final_width = display_width + margin_width  # Total canvas width

    # Create a new blank image with margin
    new_image = Image.new("RGB", (final_width, display_height), "white")
    new_image.paste(image.resize((display_width, display_height)), (0, 0))

    # Compute new scaling factors for displaying the annotated image
    scale_x = display_width / json_width
    scale_y = display_height / json_height

    # Create a drawing context
    draw = ImageDraw.Draw(new_image)

    # Font settings (Using a Unicode-compatible font)
    try:
        # Use a Unicode-supporting font (DejaVu Sans or Arial Unicode MS)
        font = ImageFont.truetype(ROOT + "/home/STual/DAN-cadastre/scripts/DAN/fonts/DejaVuSans.ttf", 25)  # Font size 30
    except:
        font = ImageFont.load_default()

    # Process each detected object
    for counter, obj in enumerate(data["objects"]):
        polygon = obj["polygon"]
        
        # Convert polygon to bounding box (xmin, ymin, xmax, ymax)
        x_coords = [p[0] for p in polygon]
        y_coords = [p[1] for p in polygon]
        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)

        # Apply full-width option
        if FULL_WIDTH_RECTANGLES:
            xmin = 0  # Extend to left edge
            xmax = json_width  # Extend to right edge

        # Rescale bounding box to match display size
        scaled_rect = (
            int(xmin * scale_x), int(ymin * scale_y), 
            int(xmax * scale_x), int(ymax * scale_y)
        )

        # Compute centroid for text alignment
        centroid_y = int((scaled_rect[1] + scaled_rect[3]) / 2)

        # Alternate rectangle colors (red & blue)
        color = "red" if counter % 2 == 0 else "blue"

        # Draw the bounding box
        draw.rectangle(scaled_rect, outline=color, width=3)

        # Draw text in the right margin at centroid height
        text_position = (display_width + 20, centroid_y - 15)  # Increased offset
        draw.text(text_position, obj["text"], fill=color, font=font)

    # Show the resized annotated image
    new_image.show()

    # Save the annotated image (optional)
    if SAVE:
        new_image.save(f"{uuid}_annotated.jpg")


def load_and_display_line_level(folder_path, index):
    """
    # Example usage: Provide the path to the folder containing JSON files and the desired index
    folder_path = '/home/STual/inference/res2'
    index_to_display = 25 # Replace with the desired index
    load_and_display_line_level(folder_path, index_to_display)
    """
    
    # Get the list of JSON files in the folder
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]

    # Ensure the provided index is valid
    if 0 <= index < len(json_files):
        # Get the JSON file path
        json_file_path = os.path.join(folder_path, json_files[index])

        # Load the JSON content
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Extract text and image paths from JSON
        text = data.get('text', '')
        image_path = data.get('attention_gif', '')

        # Print the text
        print(f"Text: {text}")

        # Load and display the image
        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            plt.figure(figsize=(10, 10))
            plt.imshow(image)
            plt.axis('off')
            plt.show()
        else:
            print("Image not found.")
    else:
        print("Invalid index.")

def restore_polygon_to_original_size(polygon, original_width, original_height, max_width=2000, max_height=3000):
    # Compute scale used during resize
    scale = min(max_width / original_width, max_height / original_height)

    # Restore coordinates
    return [[round(x / scale), round(y / scale)] for x, y in polygon]