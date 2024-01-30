import threading
from face_rec import face_recognition, sleepy_status
from data_management import load_data
from speech_recognition_response import talkback


if __name__ == "__main__":
    api_key = '3045dd712ffe6e702e3245525ac7fa38'  
    patterns_file_path = 'patterns.json'
    location_file_path = 'location.json'
    music_data = 'music_data.json'
    patterns, greetings, contacts, navigation_data, music_data, jokes = load_data(patterns_file_path, location_file_path, music_data)
    face_thread = threading.Thread(target=face_recognition)
    face_thread.start()
    talkback(api_key, patterns, greetings, contacts, navigation_data, music_data, jokes, sleepy_status)

