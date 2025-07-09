# memebot.py

import os
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from threading import Thread

# === CONFIGURAÇÃO DE LOG ===
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# === VARIÁVEIS DE AMBIENTE ===
TOKEN            = os.getenv("TOKEN")
CHAT_ID          = os.getenv("CHAT_ID")
LUNAR_API_KEY    = os.getenv("LUNAR_API_KEY")
BSCSCAN_API_KEY  = os.getenv("BSCSCAN_API_KEY")

API_DEXTOOLS     = "https://api.dexscreener.com/latest/dex/pairs/bsc"  # ✅ CORRIGIDO
LUCRO_ALVO_1     = float(os.getenv("LUCRO_ALVO_1", 100))
LUCRO_ALVO_2     = float(os.getenv("LUCRO_ALVO_2", 200))
BLACKLIST_FILE   = "blacklist.json"

tokens_monitorados = {}

# === BLACKLIST PERSISTENTE ===
try:
    with open(BLACKLIST_FILE, "r") as f:
        blacklist_tokens = set(json.load(f))
except:
    blacklist_tokens = set()

def salvar_blacklist():
    try:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(list(blacklist_tokens), f)
        logging.info("Blacklist salva.")
    except Exception as e:
        logging.error(f"Erro ao salvar blacklist: {e}")

def enviar_mensagem(texto: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        logging.info("Memebot enviou mensagem.")
    except Exception as e:
        logging.error(f"Erro ao enviar Telegram: {e}")

# === CHAMADAS COMUNS ===
def fetch_json(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

# === BUSCA DE NOVOS TOKENS ===
def buscar_tokens_novos():
    try:
        data = fetch_json(API_DEXTOOLS)
        pares = data.get("pairs", [])
        return [t for t in pares if t.get("chainId") == "bsc"]
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            logging.warning("Rate limit 429 — pausing 10min")
            time.sleep(600)
        else:
            logging.error(f"HTTP Error: {e}")
    except Exception as e:
        logging.error(f"Erro ao buscar tokens novos: {e}")
    return []

# === MONITORAMENTO CONTÍNUO ===
def acompanhar_tokens():
    while True:
        try:
            data = fetch_json(API_DEXTOOLS)
            pares = [t for t in data.get("pairs", []) if t.get("chainId") == "bsc"]

            # Checa variação para cada token já registrado
            for token in list(tokens_monitorados):
                info = tokens_monitorados[token]
                if datetime.utcnow() - info["ultima_verificacao"] > timedelta(hours=24):
                    tokens_monitorados.pop(token, None)
                    continue

            for t in pares:
                addr = t["pairAddress"]
                if addr in blacklist_tokens or addr not in tokens_monitorados:
                    continue

                preco_atual = float(t["priceUsd"])
                inicial = tokens_monitorados[addr]["preco_inicial"]
                variacao = (preco_atual - inicial) / inicial * 100

                if variacao >= LUCRO_ALVO_2 and not tokens_monitorados[addr]["alertou2"]:
                    enviar_mensagem(f"🚨 <b>+{variacao:.2f}%</b> em {t['baseToken']['symbol']} — venda sugerida.")
                    tokens_monitorados[addr]["alertou2"] = True

                elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados[addr]["alertou1"]:
                    enviar_mensagem(f"📈 +{variacao:.2f}% em {t['baseToken']['symbol']} — considerar parcial.")
                    tokens_monitorados[addr]["alertou1"] = True

                elif variacao <= -50:
                    enviar_mensagem(f"⚠️ Queda de {variacao:.2f}% em {t['baseToken']['symbol']} — possível rug pull.")

                tokens_monitorados[addr]["ultima_verificacao"] = datetime.utcnow()

        except Exception as e:
            logging.error(f"Erro em acompanhar_tokens: {e}")

        time.sleep(60)

# === LOOP PRINCIPAL ===
def iniciar_memebot():
    logging.info("🚀 Memebot iniciado.")
    Thread(target=acompanhar_tokens, daemon=True).start()

    while True:
        novos = buscar_tokens_novos()
        for t in novos:
            addr = t["pairAddress"]
            if addr in blacklist_tokens or addr in tokens_monitorados:
                continue

            # Simples validação inicial (pode estender com BSCSCAN, LUNAR etc)
            preco = float(t["priceUsd"])
            tokens_monitorados[addr] = {
                "preco_inicial": preco,
                "ultima_verificacao": datetime.utcnow(),
                "alertou1": False,
                "alertou2": False
            }

            msg = (
                f"🚨 <b>NOVO MEME COIN</b>\n\n"
                f"Token: <b>{t['baseToken']['symbol']}</b>\n"
                f"Preço: ${preco:.6f}\n"
                f"Volume 24h: ${float(t['volume']['h24']):,.0f}\n"
                f"🔗 https://dexscreener.com/bsc/{addr}"
            )
            enviar_mensagem(msg)

        time.sleep(int(os.getenv("INTERVALO_MEMEBOT", 5)) * 60)

if __name__ == "__main__":
    iniciar_memebot()
