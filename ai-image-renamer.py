import os
from dotenv import load_dotenv
import requests
from os.path import exists
from PIL import Image
import shutil
import sys
import time

load_dotenv()

# Replace with your Cognitive Services subscription key
subscription_key = os.environ.get('API_KEY')

# Replace with the desired endpoint URL
endpoint_url = os.environ.get('ENDPOINT_URL')

# Replace with the desired language code. Options: en (English),es (Spanish),ja (Japanese),pt (Portugese),zh (Chinese Simplified)
language = "en"

# Allowed image extensions
allowed_extensions = {'jpeg', 'jpg', 'png', 'gif', 'bmp'}

if len(sys.argv) < 2:
    print("usage: python script.py image_folder [recursive]")
    sys.exit()

# Get the image folder from the argument
image_folder = sys.argv[1]

def check_img_size(original_file_path, temp_file_path, file_size, max_size_mb):
    try:
        if file_size > 4 * 1024 * 1024:
            print(" - File size to large. Compressing temporary copy.")
            max_size = max_size_mb * 1024 * 1024
            ext = os.path.splitext(temp_file_path)[1]
    
            quality = 95  # Set initial compression quality to 95 (out of 100)
    
            while True:  # Start an infinite loop to iteratively compress the image
                with Image.open(original_file_path) as img:
                    print(f" - Compressing file to {quality}%...")
                    if ext.lower() in ['.jpeg', '.jpg']:  # Quality-based compression for JPEG
                        img.save(temp_file_path, 'JPEG', quality=quality)
                    else:  # Resize for other formats
                        scale_factor = quality / 100
                        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        img.save(temp_file_path)
    
                current_size = None
                current_size = os.path.getsize(temp_file_path)  # Get the file size of the compressed image
                print(f" - Resulting size is {current_size}")
    
                if current_size <= max_size:
                    print(" - Success!")
                    break
                else:
                    print(" - File still too large, decreasing quality...")
                    if current_size > max_size:
                        quality -= 5
                    if quality < 5:
                        print(" - Failed, giving up...")
                        break
    except Exception as e:
        print(f"Error in check_img_size for {original_file_path}: {e}")
        raise


def check_img_dimensions(temp_file_path):
    try:
        with Image.open(temp_file_path) as img:
            width, height = img.size
    
            # Check if either dimension is smaller than 50
            if width < 50 or height < 50:
                print(" - Image dimensions to small. Resizing temporary copy.")
                # Calculate the new size, maintaining the aspect ratio
                new_width = max(50, width)
                new_height = max(50, height)
    
                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
                # Save the resized image
                resized_img.save(temp_file_path)
                print(f" - Image resized to {new_width}x{new_height} pixels.")
    except Exception as e:
        print(f"Error in check_img_dimensions for {temp_file_path}: {e}")
        raise


# Check if recursive flag is provided
recursive = False
if len(sys.argv) > 2 and sys.argv[2] == "recursive":
    recursive = True
skipped_imgs = []
i = 1

def process_imgs(file, file_path, root):
    global i
    temp_path = os.path.join(root, f"{os.path.splitext(file)[0]}_temp{os.path.splitext(file)[1]}")
    try:
        # Creating a temporary copy of file to send to API
        shutil.copy2(file_path, temp_path)
    
        file_size = os.path.getsize(file_path)
    
        check_img_size(file_path, temp_path, file_size, 3.99)
        check_img_dimensions(temp_path)
    
        file_path = temp_path
        # Open the image file

        max_retries = 60  # Maximum number of retries
        retry_delay = 5  # Seconds to wait between retries
    
        for attempt in range(max_retries):
            try:
                with open(file_path, "rb") as image_file:
                    vision_url = endpoint_url + "/vision/v3.2/describe?language=" + language + "&model-version=latest"
                    headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
                    response = requests.post(vision_url, headers=headers, data=image_file)
                    response.raise_for_status()
                    # Get the image description from the API response
                    image_description = response.json()["description"]["captions"][0]["text"].capitalize()
                    # Create a new file name based on the image description
                    new_file_name = image_description.replace(" ", "_") + "." + file.split(".")[-1]
                    new_file_name = new_file_name.lower()
                    # Rename the image file
                    new_file_path = os.path.join(root, new_file_name)
                    #Check if files exists
                    if os.path.isfile(new_file_path):
                        print(" - File name exists. Adding suffix.")
                        new_file_name = image_description.replace(" ", "_") + '_' + str(i) + "." + file.split(".")[-1]
                        new_file_name = new_file_name.lower()
                        # Rename the image file
                        new_file_path = os.path.join(root, new_file_name)
                        os.rename(file_path, new_file_path)
                        #os.rename(file_path, new_file_path + '_' + str(i))
                        # new_file_path = new_file_path + '_' + str(i)
                        i += 1
                        print(f"Renamed '{file}' to '{new_file_name}'")
                    else:
                        os.rename(file_path, new_file_path)
                        print(f"Renamed '{file}' to '{new_file_name}'")
                    os.rename(os.path.join(root, file), new_file_path)
                break
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:  # Check if it's not the last attempt
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise

    except Exception as e:
        print(f"Error processing '{file}': {e}")
        skipped_imgs.append(file)

        if os.path.exists(temp_path):
            os.remove(temp_path)
            #print(f" - Removed temporary file for '{file}'")
    print()


if recursive:
    for root, dirs, files in os.walk(image_folder):
        for file in files:
            # Check if file has an allowed extension
            if file.split('.')[-1] in allowed_extensions:
                print(f"Processing '{file}'")
                file_path = os.path.join(root, file)
                process_imgs(file, file_path, root)
else:
    for file in os.listdir(image_folder):
        # Check if file has an allowed extension
        if file.split('.')[-1] in allowed_extensions:
            print(f"Processing '{file}'")
            file_path = os.path.join(image_folder, file)
            process_imgs(file, file_path, image_folder)


print("Done!")
if skipped_imgs:
    print("Skipped images:", skipped_imgs)

