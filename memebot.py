import json
from threading import Thread
import time
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LUNAR_API_KEY = os.getenv("LUNAR_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc?sort=recent"
LUCRO_ALVO_1 = 100
LUCRO_ALVO_2 = 200
BLACKLIST_FILE = "blacklist.json"

headers_lunar = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}

tokens_monitorados = {}

try:
    with open(BLACKLIST_FILE, "r") as f:
        blacklist_tokens = set(json.load(f))
except:
    blacklist_tokens = set()

def salvar_blacklist():
    try:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(list(blacklist_tokens), f)
    except Exception as e:
        print("Erro ao salvar blacklist:", e)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# ... (suas outras funções permanecem iguais)

# === Função buscar_tokens_novos ajustada para tratar erro 429 ===
def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        if r.status_code == 429:
            print("Rate limit 429 detectado na API Dexscreener. Pausando 10 minutos...")
            time.sleep(600)  # pausa de 10 minutos para aliviar o bloqueio
            return []
        r.raise_for_status()
        pares = r.json().get("pairs", [])
        return [t for t in pares if t.get("chainId") == "bsc"]
    except Exception as e:
        print("Erro ao buscar tokens novos:", e)
        return []

# === Função para retornar intervalo dinâmico com horários e valores solicitados ===
def intervalo_dinamico():
    agora = datetime.now()
    hora_decimal = agora.hour + agora.minute / 60
    if 6.5 <= hora_decimal <= 20.5:
        return 3  # intervalo de 3 minutos entre 6:30 e 20:30
    else:
        return 10  # intervalo de 10 minutos fora desse horário

def acompanhar_tokens():
    while True:
        try:
            r = requests.get(API_DEXTOOLS)
            if r.status_code == 429:
                print("Rate limit 429 detectado na API Dexscreener no acompanhar_tokens. Pausando 10 minutos...")
                time.sleep(600)
                continue
            r.raise_for_status()

            pares = r.json().get("pairs", [])
            tokens = [t for t in pares if t.get("chainId") == "bsc"]
            for token in tokens:
                contrato = token['pairAddress']
                if contrato in tokens_monitorados or contrato in blacklist_tokens:
                    continue
                preco_atual = float(token['priceUsd'])
                preco_inicial = tokens_monitorados.get(contrato, {}).get('preco_inicial', preco_atual)
                variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100
                nome = token['baseToken']['symbol']

                if variacao >= LUCRO_ALVO_2 and not tokens_monitorados.get(contrato, {}).get("alertou2"):
                    msg = f"\U0001F4A5 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {nome}\nVenda sugerida. Preço: ${preco_atual:.6f}"
                    enviar_mensagem(msg)
                    tokens_monitorados[contrato]["alertou2"] = True

                elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados.get(contrato, {}).get("alertou1"):
                    msg = f"📈 <b>+{variacao:.2f}%</b> em {nome}\nConsidere parcial. Preço: ${preco_atual:.6f}"
                    enviar_mensagem(msg)
                    tokens_monitorados[contrato]["alertou1"] = True

                elif variacao < -50:
                    msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {nome}\nPossível rug. Avalie saída."
                    enviar_mensagem(msg)

                if datetime.utcnow() - tokens_monitorados.get(contrato, {}).get('ultima_verificacao', datetime.utcnow()) > timedelta(hours=24):
                    tokens_monitorados.pop(contrato, None)
        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(60)  # Pode manter 60s aqui porque acompanha tokens roda em thread separada

def iniciar_memebot():
    print("🚀 Memebot iniciado com persistência de blacklist.")
    Thread(target=acompanhar_tokens, daemon=True).start()

    while True:
        intervalo = intervalo_dinamico()
        tokens = buscar_tokens_novos()
        for token in tokens:
            contrato = token['pairAddress']
            if contrato in blacklist_tokens or contrato in tokens_monitorados:
                continue
            if not analisar_token(token):
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            nome = token['baseToken']['symbol']
            preco = float(token['priceUsd'])
            mc = float(token.get('fdv', 0))
            liquidez = float(token['liquidity']['usd'])

            goplus = verificar_goplus(contrato)
            if goplus.get('result', {}).get(contrato, {}).get('is_open_source') == '0':
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            social = verificar_social_lunar(nome)
            if not social or social['social_volume'] < 500 or social['alt_rank'] > 25:
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            tokens_monitorados[contrato] = {
                "preco_inicial": preco,
                "ultima_verificacao": datetime.utcnow(),
                "alertou1": False,
                "alertou2": False,
            }

            msg = (
                f"🚨 <b>NOVO ALERTA DE MEME COIN</b>\n\n"
                f"Token: <b>{nome}</b>\n"
                f"Market Cap: ${mc:,.0f}\n"
                f"Liquidez: ${liquidez:,.0f}\n"
                f"Volume 5min: ${float(token['volume']['m5']):,.0f}\n"
                f"Volume 24h: ${float(token['volume']['h24']):,.0f}\n"
                f"Preço Inicial: ${preco:.6f}\n"
                f"🔥 Social Volume: {social['social_volume']}\n"
                f"🧠 Galaxy Score: {social['galaxy_score']}\n"
                f"📈 Alt Rank: {social['alt_rank']}\n"
                f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
            )
            enviar_mensagem(msg)

        time.sleep(intervalo * 60)  # intervalo dinâmico entre execuções

if __name__ == '__main__':
    iniciar_memebot()
