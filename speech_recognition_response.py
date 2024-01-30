import speech_recognition as sr
import pyttsx3
import pygame
import threading
from car_maintainance import car_details
from utility import (
    extract_city, get_date_time_info, control_ac, control_windows, control_doors,
    control_sunroof, play_random_song, load_music_data,handle_music_control
)
from communication import send_whatsapp_message
from location_weather import get_approximate_location, get_weather, get_current_weather
import random

play_thread = None
playing = False
def play_music(track):
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(track['path'])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  
            pygame.time.Clock().tick(10)  
    except Exception as e:
        print(f"Error playing track: {e}")

def get_random_start_road(city_data, city_name='bangalore'):
    for city in city_data:
        if city['name'].lower() == city_name.lower():
            return random.choice(city['roads'])
    return None

def get_navigation_instructions(start_road, destination_road, city_data):
    if not start_road:
        start_road = get_random_start_road(city_data)
        if not start_road:
            return "No starting road found."

    if not destination_road:
        neighboring_roads = ', '.join([neighbor['name'] for neighbor in start_road['neighboring_roads']])
        return f"Starting from {start_road['name']}, you can go to: {neighboring_roads}"

    for neighbor in start_road['neighboring_roads']:
        if neighbor['name'].lower() == destination_road.lower():
            instructions = []
            for nav in neighbor['navigation']:
                instruction = nav.get('instruction', 'Continue')  
                poi = nav.get('poi', '')  
                instruction_text = f"{instruction}"
                if poi:
                    instruction_text += f" near {poi}"
                instructions.append(instruction_text)
            return f"Starting from {start_road['name']}, " + ' '.join(instructions)
    
    return "Navigation instructions not found."


def recognize_query(tokens, patterns, greetings):
    if any(greeting.lower() in tokens for greeting_obj in greetings for greeting in greeting_obj['patterns']):
        return random.choice([greeting_obj['responses'][0] for greeting_obj in greetings])
    
    for pattern_obj in patterns:
        for pattern in pattern_obj['patterns']:
            if any(pattern_token in tokens for pattern_token in pattern.lower().split()):
                return random.choice(pattern_obj['responses'])
    
    return "I'm sorry, I don't understand that query."

engine = pyttsx3.init()
engine.setProperty('rate', 150)




def talkback(api_key, patterns, greetings, contacts, navigation_data,music_data, jokes, sleepy_status):
    recognizer = sr.Recognizer()
    

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"Recognized: '{text}'")
                if sleepy_status:
                    engine.say("Wake up ! sleep state detected, Uth re baba nai to mar jayega")
                    engine.runAndWait()

                if 'exit' in text or 'quit' in text:
                    print("Exiting...")
                    engine.say("Exiting...")
                    engine.runAndWait()
                    break

                tokens = text.split()
                response = recognize_query(tokens, patterns, greetings)

                if 'weather' in tokens:
                    city = extract_city(tokens)
                    if city:
                        response = get_current_weather(api_key, city)
                    else:
                        latitude, longitude, approx_city = get_approximate_location()
                        if latitude and longitude:
                            response = get_weather(latitude, longitude, api_key)
                        else:
                            response = "Unable to fetch current location."
                elif 'message' in tokens or 'text' in tokens:
                    contact_name = ' '.join(tokens[1:])  
                    phone_number = contacts.get(contact_name)
                    if phone_number:
                        print(f"Please say your message for {contact_name}.")
                        engine.say(f"Please say your message for {contact_name}.")
                        engine.runAndWait()
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        message_text = recognizer.recognize_google(audio).lower()
                        response = send_whatsapp_message(phone_number, message_text)
                    else:
                        response = "Contact not found."
                elif any(token in tokens for token in ['time', 'date', 'day']):
                    response = get_date_time_info(text)

                elif 'ac' in tokens:
                    action = 'on' if 'on' in tokens else 'off'
                    response = control_ac(action)
                elif 'window' in tokens:
                    action = 'open' if 'open' in tokens else 'close'
                    response = control_windows(action)
                elif 'sunroof' in tokens:
                    action = 'open' if 'open' in tokens else 'close'
                    response = control_sunroof(action)
                elif 'door' in tokens or 'doors' in tokens:
                    action = 'locked' if 'lock' in tokens else 'unlock'
                    response = control_doors(action)
                elif 'navigate' in tokens:
                    try:
                        destination_road = None
                        if 'to' in tokens:
                            dest_index = tokens.index('to') + 1
                            destination_road = ' '.join(tokens[dest_index:])

                        start_road = None

                        if 'from' in tokens:
                            start_index = tokens.index('from') + 1
                            start_road = ' '.join(tokens[start_index:tokens.index('to')]) if 'to' in tokens else ' '.join(tokens[start_index:])

                        if not start_road:
                            start_road = get_random_start_road(navigation_data)
                            neighboring_roads = ', '.join([neighbor['name'] for neighbor in start_road['neighboring_roads']])
                            print(f"Starting from {start_road['name']}, you can go to: {neighboring_roads}")
                            engine.say(f"You are currently on {start_road['name']}. Where would you like to go? Your options are: {neighboring_roads}")
                            engine.runAndWait()

            
                            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                            destination_road = recognizer.recognize_google(audio).lower()

                        response = get_navigation_instructions(start_road, destination_road, navigation_data)
                        if "traffic" in response:
                            response += " Adjusting route for faster travel."
                    except (ValueError, IndexError, sr.UnknownValueError, sr.RequestError):
                        response = "Please specify the destination road correctly."

                
                elif 'music' in tokens:
                    music_data = load_music_data('music_data.json')
                    music_command = 'play music'
                    while music_command != 'stop':
                        print("Listening Music Command...")
                        text = recognizer.recognize_google(audio).lower()
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        handle_music_control(music_command, music_data)
                        response = f"Music {music_command.replace(' music', '')}ed."
                        tokens = text.split()
                        if 'play' in tokens:
                            music_command = 'play music'
                        elif 'pause' in tokens:
                            music_command = 'pause'
                        elif 'resume' in tokens:
                            music_command = 'resume'
                        elif 'stop' in tokens:
                            music_command = 'stop'
                        if music_command:
                            handle_music_control(music_command, music_data)
                            response = f"Music {music_command.replace(' music', '')}ed."

                elif 'car' in tokens:
                    response = "What information you want to know! Fuel, Filter, Tyre Pressure, Oil "
                    engine.say(response)
                    engine.runAndWait()
                    car_details()

                elif 'joke' in tokens or 'jokes' in tokens:
                    joke = random.choice(jokes)
                    response = joke
                
                else:
                    response = "I didn't understand that. Can you please specify what information you want?"
                engine.say(response)
                engine.runAndWait()
                # response = recognize_query(tokens, patterns, greetings)
                # engine.say(response)
                # engine.runAndWait()

        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            engine.say("Sorry, I did not understand that.")
            engine.runAndWait()
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            engine.say("Sorry, my speech service is down.")
            engine.runAndWait()
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            engine.say("Listening timed out.")
            engine.runAndWait()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break






