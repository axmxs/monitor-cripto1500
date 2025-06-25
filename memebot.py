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
LUCRO_ALVO_1 = 100  # % para primeiro alerta de venda
LUCRO_ALVO_2 = 200  # % para segundo alerta
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

# Tokens monitorados após alerta
tokens_monitorados = {}

# === Envio de mensagem para o Telegram ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === Buscar tokens novos ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data['pairs']
    except:
        return []

# === Filtra tokens com potencial ===
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
        if minutos > 180:  # Token com mais de 3 horas
            return False
        return True
    except:
        return False

# === Monitora evolução dos tokens após o alerta inicial ===
def acompanhar_tokens():
    while True:
        try:
            r = requests.get(API_DEXTOOLS)
            tokens = r.json().get('pairs', [])


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
LUCRO_ALVO_1 = 100  # % para primeiro alerta de venda
LUCRO_ALVO_2 = 200  # % para segundo alerta
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

# Tokens monitorados após alerta
tokens_monitorados = {}

# === Envio de mensagem para o Telegram ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === Buscar tokens novos ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data['pairs']
    except:
        return []

# === Filtra tokens com potencial ===
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
        if minutos > 180:  # Token com mais de 3 horas
            return False
        return True
    except:
        return False

# === Monitora evolução dos tokens após o alerta inicial ===
def acompanhar_tokens():
    while True:
        try:
            r = requests.get(API_DEXTOOLS)
            tokens = r.json().get('pairs', [])
            for token in tokens:
                contrato = token['pairAddress']
                if contrato in tokens_monitorados:
                    preco_atual = float(token['priceUsd'])
                    preco_inicial = tokens_monitorados[contrato]['preco_inicial']
                    variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

                    nome = token['baseToken']['symbol']

                    if variacao >= LUCRO_ALVO_2 and not tokens_monitorados[contrato].get("alertou2"):
                        msg = f"💥 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {nome}\nVenda sugerida — forte valorização.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou2"] = True

                    elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados[contrato].get("alertou1"):
                        msg = f"📈 <b>+{variacao:.2f}%</b> em {nome}\n\nConsidere realizar parcial ou ajustar stop.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou1"] = True

                    elif variacao < -50:
                        msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {nome}\nPossível rug pull ou correção forte. Avalie saída."
                        enviar_mensagem(msg)

                    # Remove token após 6 horas
                    if datetime.utcnow() - tokens_monitorados[contrato]['ultima_verificacao'] > timedelta(hours=6):
                        del tokens_monitorados[contrato]
        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(300)

# === Início do memebot ===
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
                    f"🧠 Detecção de possível pump nas próximas horas.\n\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_ANALISE)
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
LUCRO_ALVO_1 = 100  # % para primeiro alerta de venda
LUCRO_ALVO_2 = 200  # % para segundo alerta
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

# Tokens monitorados após alerta
tokens_monitorados = {}

# === Envio de mensagem para o Telegram ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === Buscar tokens novos ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data['pairs']
    except:
        return []

# === Filtra tokens com potencial ===
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
        if minutos > 180:  # Token com mais de 3 horas
            return False
        return True
    except:
        return False

# === Monitora evolução dos tokens após o alerta inicial ===
def acompanhar_tokens():
    while True:
        try:
            r = requests.get(API_DEXTOOLS)
            tokens = r.json().get('pairs', [])
            for token in tokens:
                contrato = token['pairAddress']
                if contrato in tokens_monitorados:
                    preco_atual = float(token['priceUsd'])
                    preco_inicial = tokens_monitorados[contrato]['preco_inicial']
                    variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

                    nome = token['baseToken']['symbol']

                    if variacao >= LUCRO_ALVO_2 and not tokens_monitorados[contrato].get("alertou2"):
                        msg = f"💥 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {nome}\nVenda sugerida — forte valorização.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou2"] = True

                    elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados[contrato].get("alertou1"):
                        msg = f"📈 <b>+{variacao:.2f}%</b> em {nome}\n\nConsidere realizar parcial ou ajustar stop.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou1"] = True

                    elif variacao < -50:
                        msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {nome}\nPossível rug pull ou correção forte. Avalie saída."
                        enviar_mensagem(msg)

                    # Remove token após 6 horas
                    if datetime.utcnow() - tokens_monitorados[contrato]['ultima_verificacao'] > timedelta(hours=6):
                        del tokens_monitorados[contrato]
        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(300)

# === Início do memebot ===
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
                    f"🧠 Detecção de possível pump nas próximas horas.\n\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_ANALISE)


            
            for token in tokens:
                contrato = token['pairAddress']
                if contrato in tokens_monitorados:
                    preco_atual = float(token['priceUsd'])
                    preco_inicial = tokens_monitorados[contrato]['preco_inicial']
                    variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100

                    nome = token['baseToken']['symbol']

                    if variacao >= LUCRO_ALVO_2 and not tokens_monitorados[contrato].get("alertou2"):
                        msg = f"💥 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {nome}\nVenda sugerida — forte valorização.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou2"] = True

                    elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados[contrato].get("alertou1"):
                        msg = f"📈 <b>+{variacao:.2f}%</b> em {nome}\n\nConsidere realizar parcial ou ajustar stop.\nPreço atual: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou1"] = True

                    elif variacao < -50:
                        msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {nome}\nPossível rug pull ou correção forte. Avalie saída."
                        enviar_mensagem(msg)

                    # Remove token após 6 horas
                    if datetime.utcnow() - tokens_monitorados[contrato]['ultima_verificacao'] > timedelta(hours=6):
                        del tokens_monitorados[contrato]
        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(300)

# === Início do memebot ===
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
                    f"🧠 Detecção de possível pump nas próximas horas.\n\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_ANALISE)
