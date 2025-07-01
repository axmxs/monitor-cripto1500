import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"⚠️ Erro ao enviar mensagem Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print("❌ Erro no envio da mensagem:", e)

def main():
    print("🚀 Memebot iniciado com debug da API")

    url = "https://api.dexscreener.io/latest/dex/pairs/bsc"  # endpoint correto para BSC

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("🔍 Status da API:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            if "pairs" in data and len(data["pairs"]) > 0:
                par = data["pairs"][0]
                simbolo_base = par.get("baseToken", {}).get("symbol", "N/A")
                simbolo_quote = par.get("quoteToken", {}).get("symbol", "N/A")
                preco = par.get("priceUsd", "N/A")

                print(f"✅ Primeiro par: {simbolo_base}/{simbolo_quote} - Preço: {preco}")

                mensagem = f"""✅ <b>Memebot funcionando!</b>
Par: <b>{simbolo_base}/{simbolo_quote}</b>
Preço: <b>${preco}</b>"""
                enviar_mensagem(mensagem)
            else:
                print("⚠️ Nenhum par encontrado.")
                enviar_mensagem("⚠️ <b>Memebot ativo, mas nenhum par retornado da API.</b>")
        else:
            print("❌ Erro ao acessar API:", response.status_code)
            enviar_mensagem(f"❌ <b>Erro ao acessar API:</b> Status {response.status_code}")
    except Exception as e:
        print("❌ Erro inesperado:", e)
        enviar_mensagem(f"❌ <b>Erro inesperado no memebot:</b> {e}")

if __name__ == "__main__":
    main()
