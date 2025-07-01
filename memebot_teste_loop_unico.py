import requests
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_DEXSCREENER = "https://api.dexscreener.com/latest/dex/pairs"

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': texto,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, data=payload)
        print("✅ Mensagem enviada para Telegram.")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem Telegram: {e}")
        return False

def testar_api_dexscreener():
    try:
        print("🔍 Testando requisição para API Dexscreener...")
        resposta = requests.get(API_DEXSCREENER)
        status = resposta.status_code

        if status == 200:
            pares = resposta.json().get("pairs", [])
            qtd = len(pares)
            msg = f"✅ <b>API Dexscreener OK</b>\n{qtd} pares encontrados."
            print(msg)
        else:
            msg = f"⚠️ <b>Erro na API Dexscreener</b>\nStatus: {status}"
            print(msg)

        enviar_telegram(msg)

    except Exception as e:
        erro_msg = f"❌ <b>Erro ao acessar API:</b> {str(e)}"
        print(erro_msg)
        enviar_telegram(erro_msg)

def main():
    print("🚀 Iniciando teste da API Dexscreener...")
    testar_api_dexscreener()

if __name__ == "__main__":
    main()
