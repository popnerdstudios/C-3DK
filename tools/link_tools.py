import os
import requests 
import shutil 

def save_image(url, file_name):
    subfolder = "generated"

    # Remove any leading/trailing whitespace from file_name
    file_name = file_name.strip()

    # Create the subfolder if it doesn't exist
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    file_path = os.path.join(subfolder, file_name)

    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image successfully Downloaded:', file_path)
    else:
        print('Image Couldn\'t be retrieved')

def parse_image(string):
    url, file_name = string.split(",")
    return save_image(url, file_name)

