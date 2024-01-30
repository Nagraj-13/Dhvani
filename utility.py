from datetime import datetime, timedelta
import pygame
import random
import os
import json
import threading

play_thread = None
playing = False

def get_date_time_info(query):
    
    now = datetime.now()

    if 'time' in query:
        return now.strftime("%H:%M:%S")
    elif 'date' in query:
        return now.strftime("%Y-%m-%d")
    elif 'day' in query:
        return now.strftime("%A")
    elif 'month' in query:
        return now.strftime("%B")
    elif 'year' in query:
        return now.strftime("%Y")
    elif 'time and date' in query or 'current time and date' in query:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif 'today' in query:
        return now.strftime("%Y-%m-%d")
    elif 'tomorrow' in query:
        tomorrow = now + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    else:
        return "Sorry, I couldn't understand the date/time query."

def extract_city(tokens):
  
    if 'in' in tokens:
        index_of_in = tokens.index('in')
        if index_of_in + 1 < len(tokens):
            return tokens[index_of_in + 1]
    return None

def control_ac(action):
    return f"Air Conditioning turned {'on' if action == 'on' else 'off'}."

def control_windows(action):
    return f"Windows are now {'open' if action == 'open' else 'closed'}."

def control_sunroof(action):
    return f"Sunroof is now {'open' if action == 'open' else 'closed'}."

def control_doors(action):
    return f"Doors are now {'unlocked' if action == 'unlock' else 'locked'}."

def load_music_data(json_file):
    with open(json_file, 'r') as file:
        music_data = json.load(file)
    return music_data

# Initialize Pygame mixer
pygame.mixer.init()
def play_random_song(music_data):
    global playing
    if not music_data:
        print("No music data available.")
        return

    track = random.choice(music_data)
    try:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.load(track['path'])
        pygame.mixer.music.play()
        print(f"Playing {track['title']} by {track['artist']}")
        playing = True
        while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing track: {e}")

def handle_music_control(command, music_data):
    global playing, play_thread
    if command == 'play music':
        if not pygame.mixer.music.get_busy():
            playing = True
            play_thread = threading.Thread(target=play_random_song, args=(music_data,))
            play_thread.start()
        else:
            print("Music is already playing.")
    elif command == 'pause':
        if playing:
            pygame.mixer.music.pause()
            playing = False
        else:
            print("No music is playing.")
    elif command == 'resume':
        if not playing:
            pygame.mixer.music.unpause()
            playing = True
        else:
            print("No music is paused.")
    elif command == 'stop':
        if playing:
            pygame.mixer.music.stop()
            playing = False
            if play_thread and play_thread.is_alive():
                play_thread.join()
        else:
            print("No music is playing.")
    
