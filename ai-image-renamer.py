import os
from dotenv import load_dotenv
import requests
from os.path import exists
from PIL import Image
import shutil
import sys

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
    if file_size > 4 * 1024 * 1024:
        print(" - Compression needed.")
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


def check_img_dimensions(temp_file_path):
    with Image.open(temp_file_path) as img:
        width, height = img.size

        # Check if either dimension is smaller than 50
        if width < 50 or height < 50:
            print(" - Resizing needed.")
            # Calculate the new size, maintaining the aspect ratio
            new_width = max(50, width)
            new_height = max(50, height)

            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save the resized image
            resized_img.save(temp_file_path)
            print(f" - Image resized to {new_width}x{new_height} pixels.")


# Check if recursive flag is provided
recursive = False
if len(sys.argv) > 2 and sys.argv[2] == "recursive":
    recursive = True
i = 1
# Iterate through all files in the image folder and all subfolders if recursive flag is provided
if recursive:
    for root, dirs, files in os.walk(image_folder):
        for file in files:
            # Check if file has an allowed extension
            if file.split('.')[-1] in allowed_extensions:
                print(f"Processing {file}")
                file_path = os.path.join(root, file)
                temp_path = os.path.join(root, f"{os.path.splitext(file)[0]}_temp{os.path.splitext(file)[1]}")
 
                print(f" - Creating a temporary copy of {file} to send to API")
                shutil.copy2(file_path, temp_path)

                file_size = os.path.getsize(file_path)

                check_img_size(file_path, temp_path, file_size, 3.99)
                check_img_dimensions(temp_path)

                file_path = temp_path
                # Open the image file
                with open(file_path, "rb") as image_file:
                    # Send the image to the Computer Vision API
                    vision_url = endpoint_url+"/vision/v3.2/describe?language="+language+"&model-version=latest"
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
                        print("Renamed " + file + " to " + new_file_name)
                    else:
                        os.rename(file_path, new_file_path)
                        print("Renamed " + file + " to " + new_file_name)
                    os.rename(os.path.join(root, file), new_file_path)
                    print()
else:
    for file in os.listdir(image_folder):
        # Check if file has an allowed extension
        if file.split('.')[-1] in allowed_extensions:
            print(f"Processing {file}")
            file_path = os.path.join(image_folder, file)
            temp_path = os.path.join(image_folder, f"{os.path.splitext(file)[0]}_temp{os.path.splitext(file)[1]}")
 
            print(f" - Creating a temporary copy of {file} to send to API")
            shutil.copy2(file_path, temp_path)

            file_size = os.path.getsize(file_path)

            check_img_size(file_path, temp_path, file_size, 3.99)
            check_img_dimensions(temp_path)

            file_path = temp_path
            # Open the image file
            with open(file_path, "rb") as image_file:
                # Send the image to the Computer Vision API
                vision_url = endpoint_url+"/vision/v3.2/describe?language="+language+"&model-version=latest"
                headers = {'Ocp-Apim-Subscription-Key': subscription_key, 'Content-Type': 'application/octet-stream'}
                response = requests.post(vision_url, headers=headers, data=image_file)
                response.raise_for_status()
                # Get the image description from the API response
                image_description = response.json()["description"]["captions"][0]["text"].capitalize()
                # Create a new file name based on the image description
                new_file_name = image_description.replace(" ", "_") + "." + file.split(".")[-1]
                new_file_name = new_file_name.lower()
                # Rename the image file
                new_file_path = os.path.join(image_folder, new_file_name)
                #Check if files exists
                if os.path.isfile(new_file_path):
                    print(" - File name exists. Adding suffix.")
                    new_file_name = image_description.replace(" ", "_") + '_' + str(i) + "." + file.split(".")[-1]
                    new_file_name = new_file_name.lower()
                    # Rename the image file
                    new_file_path = os.path.join(image_folder, new_file_name)
                    os.rename(file_path, new_file_path)
                    #os.rename(file_path, new_file_path + '_' + str(i))
                    # new_file_path = new_file_path + '_' + str(i)
                    i += 1
                    print("Renamed " + file + " to " + new_file_name)
                else:
                    os.rename(file_path, new_file_path)
                    print("Renamed " + file + " to " + new_file_name)
                os.rename(os.path.join(image_folder, file), new_file_path)
                print()

print("Done!")

