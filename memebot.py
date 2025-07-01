import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Exemplo de URL de um par fixo (você pode ajustar para buscar dinamicamente se quiser)
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
            return f"🔄 Atualização: Par {par}, Preço: ${float(preco):.4f}"
        else:
            return f"⚠️ Erro {response.status_code} ao consultar a API."
    except Exception as e:
        return f"❌ Erro na requisição: {str(e)}"

def acompanhar_tokens():
    while True:
        horario = datetime.now()
        hora_decimal = horario.hour + horario.minute / 60

        if 6.5 <= hora_decimal <= 20.5:
            mensagem = obter_preco()
            print("🟢 Alerta enviado. Nova verificação em breve...")
            enviar_mensagem(mensagem)
            time.sleep(1 * 60)  # verifica a cada 3 minutos
        else:
            print("🌙 Fora do horário de verificação. Aguardando...")
            time.sleep(10 * 60)  # à noite, espera mais

def iniciar_memebot():
    print("🚀 Memebot iniciado com persistência de blacklist.")
    Thread(target=acompanhar_tokens, daemon=True).start()

    while True:
        # Aqui poderia entrar o código principal do memebot
        time.sleep(60)

if __name__ == '__main__':
    iniciar_memebot()
