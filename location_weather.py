

import requests

def get_approximate_location():
    """Gets the approximate location based on the public IP address."""
    response = requests.get('http://ipinfo.io/json')
    if response.status_code == 200:
        location_data = response.json()
        lat, lon = location_data['loc'].split(',')
        city = location_data.get('city', 'Unknown City')
        return lat, lon, city
    else:
        return None, None, None

def get_weather(latitude, longitude, weather_api_key):
    """Gets the weather information using latitude and longitude."""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        weather_description = weather_data['weather'][0]['description']
        current_temp = weather_data['main']['temp']
        return f"Current weather is {weather_description} with a temperature of {current_temp}°C"
    else:
        return "Weather data not available."

def get_current_weather(api_key, city):
    """Gets the current weather information for a specified city."""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    try:
        response = requests.get(url)
        weather_data = response.json()
        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description']
        return f"Current weather in {city}: Temperature - {temperature}°C, Description - {description}"
    except Exception as e:
        return f"Error fetching weather data: {e}"
