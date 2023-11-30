import os
import requests
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_to_telegram(message, chatID):
    apiURL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    chatID = chatID.strip()
    
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

def parse_telegram_send(string):
    message, chatID = string.split("@@@")
    return send_to_telegram(message, chatID)

