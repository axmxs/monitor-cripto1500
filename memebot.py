# memebot.py (versão V3) - Rede BNB Chain

import time
import threading
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ===== CONFIGURAÇÕES =====
INTERVALO_ANALISE = 180  # em segundos (3 minutos)
LUCRO_ALVO_1 = 100       # % para primeiro alerta de venda
LUCRO_ALVO_2 = 200       # % para segundo alerta
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"
API_SOCIAL = "https://api.coinbrain.com/social-scan"  # (mock/placeholder)
API_CANDLES = "https://api.dexscreener.com/stats/candles?pairAddress={contract}&interval=1m"

# Tokens monitorados após alerta (estrutura: {contract: {"preco_inicial": float, "ultima_verificacao": timestamp}})
tokens_monitorados = {}

# === Envio de mensagem Telegram ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === Buscar tokens novos via DEXTools ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data['pairs']
    except:
        return []

# === Análise social ===
def analisar_rede_social(symbol):
    try:
        # Modo simulado (em versões futuras usar API real como LunarCrush, Coinbrain, etc)
        mencoes = symbol.lower().count("pepe") + 4  # mock
        engajamento = 80 if "pepe" in symbol.lower() else 10
        return mencoes > 3 and engajamento > 50
    except:
        return False

# === Análise técnica ===
def analise_tecnica(contrato):
    try:
        url = API_CANDLES.format(contract=contrato)
        r = requests.get(url)
        candles = r.json().get("candles", [])[-5:]

        if len(candles) < 5:
            return False

        altas = 0
        volumes = []
        corpos = []

        for c in candles:
            open_ = float(c['open'])
            close = float(c['close'])
            volume = float(c['volume'])
            corpo = abs(close - open_)

            if close > open_:
                altas += 1
            volumes.append(volume)
            corpos.append(corpo)

        volume_crescente = volumes == sorted(volumes)
        media_corpo = sum(corpos[:-1]) / 4
        ultimo_corpo = corpos[-1]

        pavio = float(candles[-1]['high']) - float(candles[-1]['close'])
        rejeicao = pavio > ultimo_corpo * 0.7

        return altas >= 3 and ultimo_corpo > 2 * media_corpo and volume_crescente and not rejeicao
    except:
        return False

# === Verifica se o token é novo e seguro ===
def analisar_token(token):
    try:
        if token['chainId'] != 'bsc':
            return False
        if not token.get("baseToken") or not token.get("quoteToken"):
            return False
        if float(token['liquidity']['usd']) < 50000:
            return False
        if float(token['fdv']) > 300000:
            return False
        if float(token['priceUsd']) <= 0:
            return False
        minutos = (datetime.utcnow() - datetime.strptime(token['pairCreatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() / 60
        if minutos > 180:
            return False

        # Novas verificacoes
        symbol = token['baseToken']['symbol']
        contrato = token['pairAddress']

        if not analisar_rede_social(symbol):
            return False

        if not analise_tecnica(contrato):
            return False

        return True
    except:
        return False

# === Monitorar tokens após alerta ===
def acompanhar_tokens():
    while True:
        for contrato, info in list(tokens_monitorados.items()):
            try:
                r = requests.get(API_DEXTOOLS)
                tokens = r.json().get('pairs', [])
                for token in tokens:
                    if token['pairAddress'] == contrato:
                        preco_atual = float(token['priceUsd'])
                        preco_inicial = info['preco_inicial']
                        variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

                        if variacao >= LUCRO_ALVO_2 and not info.get("alertou2"):
                            msg = f"💥 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {token['baseToken']['symbol']}\nVenda sugerida — forte valorização.\nPreço atual: ${preco_atual:.6f}"
                            enviar_mensagem(msg)
                            tokens_monitorados[contrato]["alertou2"] = True

                        elif variacao >= LUCRO_ALVO_1 and not info.get("alertou1"):
                            msg = f"📈 <b>+{variacao:.2f}%</b> em token {token['baseToken']['symbol']}\n\nConsidere realizar parcial ou ajustar stop.\nPreço atual: ${preco_atual:.6f}"
                            enviar_mensagem(msg)
                            tokens_monitorados[contrato]["alertou1"] = True

                        elif variacao < -50:
                            msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {token['baseToken']['symbol']}\nPossível reversão ou rug. Avalie saída."
                            enviar_mensagem(msg)

                        # Limpeza após 6h
                        if datetime.utcnow() - info['ultima_verificacao'] > timedelta(hours=6):
                            del tokens_monitorados[contrato]
            except Exception as e:
                print("Erro ao monitorar token:", e)

        time.sleep(300)

# === Iniciar análise e alertas ===
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

                msg = (
                    f"🚨 <b>NOVO ALERTA DE MEME COIN</b>\n\n"
                    f"Token: <b>{nome}</b>\n"
                    f"Market Cap: ${mc:,.0f}\n"
                    f"Liquidez: ${liquidez:,.0f}\n"
                    f"Preço Inicial: ${preco:.6f}\n"
                    f"🧠 Detecção com base em redes sociais + gráfico de alta\n\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_ANALISE)
