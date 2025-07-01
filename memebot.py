import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_DEXSCREENER = "https://api.dexscreener.com/latest/dex/pairs/bsc"

LIQUIDEZ_MINIMA = 10000  # Exemplo: apenas pares com pelo menos $10.000 em liquidez

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("❌ Erro ao enviar mensagem:", response.text)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def buscar_pares_recentes():
    try:
        response = requests.get(API_DEXSCREENER, timeout=10)
        if response.status_code != 200:
            print("⚠️ Erro ao consultar a API:", response.status_code)
            return []

        data = response.json().get("pairs", [])
        pares_filtrados = []

        for par in data:
            try:
                simbolo = par["baseToken"]["symbol"]
                quote = par["quoteToken"]["symbol"]
                preco = float(par["priceUsd"])
                liquidez = float(par["liquidity"]["usd"])
                link = f"https://dexscreener.com/bsc/{par['pairAddress']}"

                if liquidez >= LIQUIDEZ_MINIMA and preco > 0:
                    pares_filtrados.append({
                        "simbolo": simbolo,
                        "quote": quote,
                        "preco": preco,
                        "liquidez": liquidez,
                        "link": link
                    })

            except Exception as e:
                continue  # Ignora pares com dados inválidos

        return pares_filtrados

    except Exception as e:
        print("❌ Erro ao buscar pares:", e)
        return []

def intervalo_dinamico():
    agora = datetime.now()
    hora = agora.hour + agora.minute / 60
    if 6.5 <= hora <= 20.5:
        return 3  # minutos
    else:
        return 10  # fora do horário ativo

def iniciar_monitoramento():
    print("🚀 Memebot ativo. Monitorando pares recentes da BSC...")
    while True:
        pares = buscar_pares_recentes()

        for par in pares[:3]:  # Envia só os 3 primeiros pares com melhor liquidez
            mensagem = (
                f"📡 <b>NOVO PAR DETECTADO</b>\n"
                f"Token: <b>{par['simbolo']}/{par['quote']}</b>\n"
                f"Preço: ${par['preco']:.6f}\n"
                f"💧 Liquidez: ${par['liquidez']:.2f}\n"
                f"🔗 <a href='{par['link']}'>Ver no Dexscreener</a>"
            )
            enviar_mensagem(mensagem)

        tempo = intervalo_dinamico()
        print(f"🕒 Aguardando {tempo} minutos para nova verificação...\n")
        time.sleep(tempo * 60)

if __name__ == '__main__':
    iniciar_monitoramento()
