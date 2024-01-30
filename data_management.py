import json

def load_data(file_path, loc_file, music_data):
    with open(file_path, 'r') as file:
        data = json.load(file)
    with open(loc_file, 'r') as f:
        loc_data = json.load(f)
    location = loc_data.get('cities', [])
    patterns = data.get('patterns', [])
    greetings = data.get('greetings', [])
    contacts = data.get('contacts', {})
    navigation_data = loc_data.get('cities', []) 

    with open(music_data, 'r') as file:
        music_data = json.load(file)
    with open('jokes_dataset.json','r') as file:
        jokes=json.load(file)
    return patterns, greetings, contacts, navigation_data, music_data , jokes

