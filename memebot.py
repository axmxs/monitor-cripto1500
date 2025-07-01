import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_DEXSCREENER = "https://api.dexscreener.com/latest/dex/pairs/bsc"
LIQUIDEZ_MINIMA = 10000

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def buscar_pares_recentes():
    try:
        response = requests.get(API_DEXSCREENER, timeout=10)
        if response.status_code != 200:
            print("⚠️ Erro na API:", response.status_code)
            return []

        pares = []
        for par in response.json().get("pairs", []):
            try:
                preco = float(par["priceUsd"])
                liquidez = float(par["liquidity"]["usd"])
                if liquidez >= LIQUIDEZ_MINIMA and preco > 0:
                    pares.append({
                        "simbolo": par["baseToken"]["symbol"],
                        "quote": par["quoteToken"]["symbol"],
                        "preco": preco,
                        "liquidez": liquidez,
                        "link": f"https://dexscreener.com/bsc/{par['pairAddress']}"
                    })
            except:
                continue
        return pares
    except Exception as e:
        print("❌ Erro ao buscar pares:", e)
        return []

def intervalo_dinamico():
    hora = datetime.now().hour + datetime.now().minute / 60
    return 3 if 6.5 <= hora <= 20.5 else 10

def iniciar_memebot():
    print("🚀 Memebot iniciado.")
    while True:
        pares = buscar_pares_recentes()
        for par in pares[:3]:
            mensagem = (
                f"📡 <b>NOVO PAR DETECTADO</b>\n"
                f"Token: <b>{par['simbolo']}/{par['quote']}</b>\n"
                f"Preço: ${par['preco']:.6f}\n"
                f"💧 Liquidez: ${par['liquidez']:.2f}\n"
                f"🔗 <a href='{par['link']}'>Ver no Dexscreener</a>"
            )
            enviar_mensagem(mensagem)
        tempo = intervalo_dinamico()
        print(f"🕒 Aguardando {tempo} minutos...\n")
        time.sleep(tempo * 60)
