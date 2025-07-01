import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL_DEX = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x0eD7e52944161450477ee417DE9Cd3a859b14fD0"

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def obter_preco():
    try:
        response = requests.get(URL_DEX, timeout=10)
        if response.status_code == 200:
            data = response.json()
            par = data["pair"]["baseToken"]["symbol"] + "/" + data["pair"]["quoteToken"]["symbol"]
            preco = data["pair"]["priceUsd"]
            return f"🔄 Atualização: Par {par}, Preço: ${float(preco):.2f}"
        else:
            return f"⚠️ Erro {response.status_code} ao consultar a API."
    except Exception as e:
        return f"❌ Erro na requisição: {str(e)}"

def main():
    enviar_mensagem("🚀 Iniciando loop de teste da API Dexscreener")
    while True:
        mensagem = obter_preco()
        print(mensagem)
        enviar_mensagem(mensagem)
        time.sleep(60)  # aguarda 60 segundos

