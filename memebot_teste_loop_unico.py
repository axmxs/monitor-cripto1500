import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_DEXSCREENER = "https://api.dexscreener.com/latest/dex/pairs/bsc/0x0eD7e52944161450477ee417DE9Cd3a859b14fD0"  # WBNB/BUSD

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
            dados = resposta.json().get("pair", {})
            nome = dados.get("baseToken", {}).get("symbol", "Desconhecido") + "/" + dados.get("quoteToken", {}).get("symbol", "???")
            preco = dados.get("priceUsd", "N/A")
            msg = f"✅ <b>API OK</b>\nPar: <b>{nome}</b>\nPreço: <b>${preco}</b>"
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
    print("🚀 Iniciando teste da API Dexscreener com par real...")
    testar_api_dexscreener()

if __name__ == "__main__":
    main()
