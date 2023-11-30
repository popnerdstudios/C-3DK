import json

def get_contacts(_=None):
    file_path = 'data/contacts.json'  
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}.")
        return None
