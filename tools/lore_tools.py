def get_lore(_=None):
    with open('lore.txt', 'r') as file:
        return file.read()
