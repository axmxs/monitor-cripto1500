# memebot.py
import time
import threading
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# carregar variáveis .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ... (todo o restante do código do Memebot aqui)

def iniciar_memebot():
    print("🚀 Memebot iniciado.")
    threading.Thread(target=acompanhar_tokens, daemon=True).start()
    while True:
        # ... restante da função
