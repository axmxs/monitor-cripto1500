import time
import requests

# === CONFIGURAÇÕES ===
TOKEN = '7581368628:AAFr6Yy13gar8Ege40Rzaa7q_uJBTW7WSdI'  # Seu token do bot
CHAT_ID = '556381811'  # Seu ID do Telegram
INTERVALO_MINUTOS = 2  # Intervalo de envio em minutos

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

while True:
    enviar_mensagem("✅ Bot ativo — mensagem automática de teste a cada 2 minutos.")
    print("Mensagem enviada! Aguardando 2 minutos...")
    time.sleep(INTERVALO_MINUTOS * 60)
