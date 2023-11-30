import os
import requests 
import shutil 
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import re

api_key = os.getenv('GOOGLE_API_KEY')
cse_id = os.getenv('GOOGLE_CSE_ID')

def get_links(query):
    url = "https://www.googleapis.com/customsearch/v1"

    # Parameters for the API request
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': 3
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  

    search_results = response.json()
    links = [item['link'] for item in search_results.get('items', [])]

    return links

def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Remove HTML tags using a regular expression
        text = re.sub('<[^<]+?>', '', response.text)
        
        # Optionally, remove additional whitespace
        text = re.sub('\s+', ' ', text).strip()

        return text
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"

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

    else:
        print('Image Couldn\'t be retrieved')

def parse_image(string):
    url, file_name = string.split(",")
    return save_image(url, file_name)

