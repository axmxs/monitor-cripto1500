# === memebot.py (versão 2 com melhorias) ===
import time
import threading
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === CONFIG ===
INTERVALO_ANALISE = 180  # segundos (3min)
LUCRO_ALVO_1 = 100
LUCRO_ALVO_2 = 200
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"
LIMITE_MAX_LIQUIDEZ = 500_000  # não analisar moedas grandes
LIMITE_MIN_LIQUIDEZ = 40_000   # ignora moedas com pouca liquidez

# Tokens em acompanhamento após alerta
tokens_monitorados = {}

# === TELEGRAM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# === Análise de token ===
def analisar_token(token):
    try:
        if token['chainId'] != 'bsc':
            return False
        if not token.get("baseToken") or not token.get("quoteToken"):
            return False
        if float(token['priceUsd']) <= 0:
            return False

        minutos = (datetime.utcnow() - datetime.strptime(token['pairCreatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() / 60
        if minutos > 90:
            return False

        liquidez = float(token['liquidity']['usd'])
        mc = float(token.get('fdv', 0))
        if liquidez < LIMITE_MIN_LIQUIDEZ or liquidez > LIMITE_MAX_LIQUIDEZ:
            return False
        if mc > 400_000:
            return False

        return True
    except:
        return False

# === Buscar tokens novos ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data.get('pairs', [])
    except:
        return []

# === Acompanhar tokens após alerta ===
def acompanhar_tokens():
    while True:
        for contrato, info in list(tokens_monitorados.items()):
            try:
                r = requests.get(API_DEXTOOLS)
                tokens = r.json().get('pairs', [])
                for token in tokens:
                    if token['pairAddress'] != contrato:
                        continue
                    preco_atual = float(token['priceUsd'])
                    preco_inicial = info['preco_inicial']
                    variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

                    if variacao >= LUCRO_ALVO_2 and not info.get("alertou2"):
                        enviar_mensagem(
                            f"💥 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {token['baseToken']['symbol']}\nVenda sugerida!\n\n🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>")
                        tokens_monitorados[contrato]["alertou2"] = True

                    elif variacao >= LUCRO_ALVO_1 and not info.get("alertou1"):
                        enviar_mensagem(
                            f"📈 <b>+{variacao:.2f}%</b> em {token['baseToken']['symbol']}\nConsidere venda parcial.\n\n🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Gráfico</a>")
                        tokens_monitorados[contrato]["alertou1"] = True

                    elif variacao < -50:
                        enviar_mensagem(
                            f"⚠️ <b>QUEDA {variacao:.2f}%</b> em {token['baseToken']['symbol']}\nAtenção para possível RUG.\n\n🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Gráfico</a>")

                # Expira após 6h
                if datetime.utcnow() - info['ultima_verificacao'] > timedelta(hours=6):
                    del tokens_monitorados[contrato]
            except Exception as e:
                print("Erro no acompanhamento:", e)

        time.sleep(180)

# === Iniciar Bot ===
def iniciar_memebot():
    print("🚀 Memebot iniciado.")
    threading.Thread(target=acompanhar_tokens, daemon=True).start()

    while True:
        tokens = buscar_tokens_novos()
        for token in tokens:
            if not analisar_token(token):
                continue

            contrato = token['pairAddress']
            nome = token['baseToken']['symbol']
            preco = float(token['priceUsd'])
            mc = float(token.get('fdv', 0))
            liquidez = float(token['liquidity']['usd'])

            if contrato not in tokens_monitorados:
                tokens_monitorados[contrato] = {
                    "preco_inicial": preco,
                    "ultima_verificacao": datetime.utcnow(),
                }
                enviar_mensagem(
                    f"🚨 <b>ALERTA NOVA MEME COIN</b>\n\nToken: <b>{nome}</b>\nMC: ${mc:,.0f}\nLiquidez: ${liquidez:,.0f}\nInicial: ${preco:.6f}\n\n🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Gráfico</a>")

        time.sleep(INTERVALO_ANALISE)
