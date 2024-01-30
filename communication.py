    
import logging
import pywhatkit

def send_whatsapp_message(phone_number, message):
    try:
       
        if not phone_number.startswith("+"):
            raise ValueError("Phone number must be in international format and start with '+'")

        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=20, tab_close=True)
        return "Message sent successfully."
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        return f"Failed to send message: {e}"




