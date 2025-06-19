from flask import Flask
from threading import Thread
import time
import requests
import os

# === CONFIGURAÇÕES SEGURAS ===
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
INTERVALO_MINUTOS = 2

# === FLASK PARA UPTIMEROBOT ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitor está rodando.'

def manter_online():
    app.run(host='0.0.0.0', port=3000)

# === ENVIO DE MENSAGEM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === LOOP PRINCIPAL ===
def iniciar_monitoramento():
    while True:
        enviar_mensagem("✅ Bot ativo — mensagem automática de teste a cada 2 minutos.")
        print("Mensagem enviada. Aguardando...")
        time.sleep(INTERVALO_MINUTOS * 60)

# === EXECUÇÃO ===
if __name__ == '__main__':
    Thread(target=manter_online).start()
    iniciar_monitoramento()
