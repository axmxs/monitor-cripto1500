from flask import Flask
from threading import Thread
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações via variáveis de ambiente
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO_MINUTOS = 2

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitor está rodando.'

def manter_online():
    app.run(host='0.0.0.0', port=3000)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def iniciar_monitoramento():
    while True:
        enviar_mensagem("✅ Bot ativo — mensagem automática a cada 2 minutos.")
        print("Mensagem enviada. Aguardando...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == '__main__':
    Thread(target=manter_online).start()
    iniciar_monitoramento()
