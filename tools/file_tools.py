import os

def save_file(content, file_name):
    subfolder = "generated"
    file_name = file_name.strip()

    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    file_path = os.path.join(subfolder, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)



def parse_file(string):
    content, file_name = string.split("@@@")
    return save_file(content, file_name)