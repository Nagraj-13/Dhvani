import json
import pyttsx3
import speech_recognition as sr
import random

def load_dataset(json_file):
    try:
        with open(json_file, 'r') as file:
            dataset = json.load(file)
        return dataset
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found. Make sure it's in the correct directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: There was an issue decoding the JSON file {json_file}. Please check its syntax.")
        return None

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening... (say 'exit' to quit)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("👂 Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def handle_query(query, car_details, fallback_responses):
    for entry in car_details:
        for keyword in entry["keywords"]:
            if keyword in query:
                speak(random.choice(entry["response"]))
                return True
    speak(random.choice(fallback_responses))
    return False

def car_details():
    json_file = 'car_maintenance_dataset.json'
    dataset = load_dataset(json_file)

    if dataset is None:
        print("Exiting the program due to an error.")
        return

    car_details = dataset["car_details"]
    fallback_responses = dataset["fallback_responses"]

    speak("Hello, I am your car maintenance and diagnostics assistant. How can I help you today?")

    
    user_input = listen()
    handle_query(user_input, car_details, fallback_responses)
