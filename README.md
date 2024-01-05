_Remarks:_
* Forked from https://github.com/frappierer/ai-image-renamer, who made it work with the new API.
* API doesn't allow for the images file size must be less than 4MB or the images dimensions to be less than 50x50. So, the point of this fork is to fix that annoyance by creating a temporary copy of each thats meets these requirements and sending that to the API.
* The API is not the most accurate but its all we got for mass renaming images with AI (still looking for better options).
* i am a bad coder....

# AI-Image-Renamer
This repository contains a Python script that utilizes AI to automatically rename images based on their content. The script leverages the Microsoft Cognitive Services Computer Vision API to extract image descriptions and uses them to create new, more meaningful file names.

## Getting Started

### Prerequisites
- Python 3.x
- A Microsoft Cognitive Services subscription key
- PIL library
- Optional (Recommended): python-dotenv

### Installation
- Clone or download the repository
- Install PIL by running `pip install pillow`
- Now you have two options:
- Option 1: Install python-dotenv by running `pip install python-dotenv` and delcare your variables in a .env file in the same directory as the script file like so:
  ```
  API_KEY="your_subscription_key_here"
  ENDPOINT_URL="your_endpoint_url_here"
  ```
- Option 2: Remove the `from dotenv import load_dotenv` and `load_dotenv()` lines from the script and replace the values of `subscription_key` and `endpoint_url` with your actual subscription key and desired endpoint URL.

### Usage
- Run the script with the command `python script.py image_folder [recursive]`

- `image_folder` is the path to the folder containing your images
- `recursive` is an optional argument that, if provided, will make the script search for images in all subfolders.

![GIF Recording 2023-01-20 at 12 09 14 PM](https://user-images.githubusercontent.com/4376185/213681784-d0140bf8-9a12-43de-9340-ec16767629d8.gif)


### Examples
Default: `python3 ai-image-renamer.py "/Users/martinaltmann/Downloads/Website images cleaned/test"` will rename all images in that folder

Recursive: `python3 ai-image-renamer.py "/Users/martinaltmann/Downloads/Website images cleaned/test" recursive` will rename all images in that folder + subfolders

## Note
If the image already exists it will add a running number to it. Eg. You have three images with with a table and glass on it. The AI will create "table_with_glas_on_it" for the first and "table_with_glas_on_it_1" for the second. By this its not overwriting the images.

## Built With
- [Python3](https://www.python.org/)
- [Microsoft Cognitive Services Computer Vision API v3.2](https://westus.dev.cognitive.microsoft.com/docs/services/computer-vision-v3-2) - AI image analysis
