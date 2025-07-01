import time
import os
import requests
import json
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
        print(f"📤 Mensagem enviada ao Telegram. Status: {r.status_code}")
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def analisar_token(token):
    try:
        volume_5min = float(token.get("volume", {}).get("m5", 0))
        volume_24h = float(token.get("volume", {}).get("h24", 0))
        liquidez = float(token.get("liquidity", {}).get("usd", 0))
        market_cap = float(token.get("fdv", 0))
        preco = float(token.get("priceUsd", 0))

        # Critérios de filtro
        if preco <= 0: return False
        if liquidez < 1000: return False
        if market_cap < 10000 or market_cap > 10_000_000: return False
        if volume_5min < 500: return False
        if volume_24h < 3000: return False

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
            print(f"🌐 Status da API: {r.status_code}")
            
            if r.status_code != 200:
                print("❌ Erro na resposta da API.")
                time.sleep(60)
                continue

            dados = r.json()

            # 🔎 DEBUG COMPLETO — mostra os primeiros 3 pares da resposta
            if "pairs" in dados:
                print(f"🔢 Total de pares retornados: {len(dados['pairs'])}")
                print("🔍 Exemplo de pares recebidos (limite 3):")
                for p in dados['pairs'][:3]:
                    print(json.dumps(p, indent=2))
            else:
                print("⚠️ Campo 'pairs' ausente no JSON da API!")
                print("Resposta completa:", json.dumps(dados, indent=2))

            pares = dados.get("pairs", [])
            bsc_tokens = [t for t in pares if t.get("chainId") == "bsc"]

            print(f"🟡 Tokens BSC detectados: {len(bsc_tokens)}")

            for token in bsc_tokens:
                nome = token.get("baseToken", {}).get("symbol", "???")
                contrato = token.get("pairAddress", "")

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
                    print(f"✅ Alerta enviado: {nome}")
                else:
                    print(f"❌ Ignorado: {nome}")

        except Exception as e:
            print("💥 Erro na requisição principal:", e)

        time.sleep(60)
