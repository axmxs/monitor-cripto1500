import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs"

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, data=payload)
        if not r.ok:
            print("Erro Telegram:", r.text)
    except Exception as e:
        print("Erro ao enviar para Telegram:", e)

def analisar_token(token):
    try:
        nome = token.get("baseToken", {}).get("symbol", "???")
        volume_5min = float(token.get("volume", {}).get("m5", 0))
        volume_24h = float(token.get("volume", {}).get("h24", 0))
        mc = float(token.get("fdv", 0))
        liquidez = float(token.get("liquidity", {}).get("usd", 0))
        preco = float(token.get("priceUsd", 0))
        idade = token.get("pairCreatedAt", "")

        minutos = (datetime.utcnow() - datetime.strptime(idade, '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() / 60

        if volume_5min >= 3000 and volume_24h >= 10000 and liquidez > 10000 and mc < 300000 and preco > 0 and 5 < minutos < 30:
            return True
    except Exception as e:
        print("Erro ao analisar token:", e)
    return False

def main():
    enviar_mensagem("🔍 Debug: memebot rodando com sucesso")

    while True:
        print(f"[{datetime.now()}] 🔁 Buscando tokens novos...")
        try:
            r = requests.get(API_DEXTOOLS)
            pares = r.json().get("pairs", [])
            bsc_tokens = [t for t in pares if t.get("chainId") == "bsc"]

            print(f"🔢 Total BSC tokens encontrados: {len(bsc_tokens)}")

            for token in bsc_tokens:
                contrato = token.get("pairAddress", "")
                nome = token.get("baseToken", {}).get("symbol", "???")

                if analisar_token(token):
                    msg = (
                        f"🚀 <b>MemeCoin Detectada</b>\n"
                        f"Token: {nome}\n"
                        f"Market Cap: ${float(token.get('fdv', 0)):,}\n"
                        f"Liquidez: ${float(token.get('liquidity', {}).get('usd', 0)):,}\n"
                        f"Volume 5min: ${float(token['volume']['m5']):,.0f}\n"
                        f"Volume 24h: ${float(token['volume']['h24']):,.0f}\n"
                        f"Preço: ${float(token.get('priceUsd', 0)):.6f}\n"
                        f"⏱️ Criado há poucos minutos\n"
                        f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                    )
                    enviar_mensagem(msg)
                    print(f"✅ Enviado alerta de: {nome}")
                else:
                    print(f"❌ Ignorado: {nome}")
        except Exception as e:
            print("Erro principal:", e)

        time.sleep(60)
