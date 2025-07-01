import requests
import time
import os

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem no Telegram:", e)

def main():
    print("🚀 Memebot iniciado com debug da API")
    url = "https://api.dexscreener.com/latest/dex/pairs"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0; +https://github.com/axmxs/monitor-cripto1500)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("🔍 Status da API:", response.status_code)

        if response.status_code == 200:
            # Imprime parte da resposta bruta
            print("🧪 Conteúdo bruto da resposta (500 chars):")
            print(response.text[:500])

            data = response.json()
            if "pairs" in data and len(data["pairs"]) > 0:
                par_exemplo = data["pairs"][0]
                print("✅ Primeiro par encontrado:", par_exemplo.get("baseToken", {}).get("symbol"), "/", par_exemplo.get("quoteToken", {}).get("symbol"))
                enviar_mensagem("✅ <b>Memebot rodando e API funcionando!</b>\nPrimeiro par: " + str(par_exemplo.get("baseToken", {}).get("symbol")))
            else:
                print("⚠️ Nenhum par encontrado na resposta da API.")
                enviar_mensage_
