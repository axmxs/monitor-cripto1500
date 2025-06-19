import time
import requests

# === CONFIGURAÇÕES ===
TOKEN = '7581368628:AAFr6Yy13gar8Ege40Rzaa7q_uJBTW7WSdI'
CHAT_ID = '556381811'
INTERVALO_MINUTOS = 2  # Envia mensagem a cada 2 minutos

# === Função de envio para o Telegram ===
def enviar_mensagem(texto):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': texto,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=payload)
        print(f"Mensagem enviada: {texto}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# === Loop de teste contínuo ===
if __name__ == '__main__':
    contador = 1
    while True:
        mensagem = f"🟢 <b>Teste de atividade #{contador}</b>\nReplit está ativo ✅\n{time.ctime()}"
        enviar_mensagem(mensagem)
        contador += 1
        time.sleep(INTERVALO_MINUTOS * 60)
