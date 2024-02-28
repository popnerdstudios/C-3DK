import os

def save_file(content, file_name):
    subfolder = "generated"
    file_name = file_name.strip()

    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    file_path = os.path.join(subfolder, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    return content

def read_file(file_name):
    subfolder = "generated"
    file_name = file_name.strip()

    file_path = os.path.join(subfolder, file_name)

    with open(file_path, 'r') as file:
        content = file.read()
    return content

def edit_file(file_name, old_text, new_text):
    subfolder = "generated"
    file_name = file_name.strip()

    file_path = os.path.join(subfolder, file_name)
    with open(file_path, 'r') as file:
        content = file.read()
        content = content.replace(old_text, new_text)
    with open(file_path, 'w') as file:
        file.write(content) 
    return content

def parse_file(string):
    content, file_name = string.split("@@@")
    return save_file(content, file_name)



