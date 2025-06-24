import time
import threading
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== CONFIGURAÇÕES =====
INTERVALO_ANALISE = 180  # em segundos (3 minutos)
LUCRO_ALVO_1 = 100       # % para primeiro alerta de venda
LUCRO_ALVO_2 = 200       # % para segundo alerta de venda
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

# Tokens em aco
