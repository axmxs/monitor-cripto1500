from flask import Flask
from threading import Thread
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURAÇÕES ===
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO_MINUTOS = 5

# === FLASK APP ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitor está rodando.'

# === ENVIO DE MENSAGEM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === LOOP DE MONITORAMENTO EM BACKGROUND ===
def iniciar_monitoramento():
    while True:
        enviar_mensagem("✅ Bot ativo — mensagem automática de teste a cada 5 minutos.")
        print("Mensagem enviada.")
        time.sleep(INTERVALO_MINUTOS * 60)

# === INÍCIO ===
if __name__ == '__main__':
    # Inicia a thread que envia mensagens
    Thread(target=iniciar_monitoramento).start()

    # Executa o Flask na thread principal
    app.run(host='0.0.0.0', port=3000)

