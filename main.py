from flask import Flask
from threading import Thread
import time
import requests

# === CONFIGURAÇÕES ===
TOKEN = '7581368628:AAFr6Yy13gar8Ege40Rzaa7q_uJBTW7WSdI'
CHAT_ID = '556381811'
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
