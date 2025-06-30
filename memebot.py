import time
import threading
import requests
import json
from datetime import datetime

BLACKLIST_FILE = "blacklist.json"
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

INTERVALO_MINUTOS = 3  # Roda de 3 em 3 minutos

def carregar_blacklist():
    try:
        with open(BLACKLIST_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def salvar_blacklist(blacklist):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(blacklist), f)

def buscar_tokens_novos():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        r = requests.get(API_DEXTOOLS, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[memebot] Erro HTTP {r.status_code} ao buscar tokens.")
            return []
        try:
            return r.json().get("pairs", [])
        except json.JSONDecodeError:
            print(f"[memebot] Erro: resposta não é JSON. Conteúdo: {r.text[:200]}")
            return []
    except Exception as e:
        print("[memebot] Erro ao buscar tokens novos:", e)
        return []

def analisar_token(token):
    try:
        # Lógica de exemplo (você pode expandir com seus critérios)
        price_usd = float(token.get("priceUsd", 0))
        tx_count = int(token.get("txCount", 0))
        if price_usd > 0 and tx_count > 10:
            return True
    except Exception as e:
        print("[memebot] Erro ao analisar token:", e)
    return False

def iniciar_monitoramento():
    print("[memebot] Thread de monitoramento iniciada.")
    blacklist = carregar_blacklist()

    while True:
        print("[memebot] Buscando tokens para monitorar...")
        tokens = buscar_tokens_novos()
        print(f"[memebot] {len(tokens)} tokens recebidos.")

        novos = 0
        for token in tokens:
            token_id = token.get("pairAddress")
            if not token_id or token_id in blacklist:
                continue

            if analisar_token(token):
                print(f"🟢 Token interessante encontrado: {token.get('baseToken', {}).get('symbol')} - {token.get('pairAddress')}")
                # Aqui você pode enviar para Telegram, Discord, etc.

                blacklist.add(token_id)
                novos += 1

        salvar_blacklist(blacklist)

        if novos == 0:
            print("⏸️ Dados insuficientes para envio (ativos com preço válido insuficiente).")

        print(f"[memebot] Intervalo de busca: {INTERVALO_MINUTOS} minutos")
        time.sleep(INTERVALO_MINUTOS * 60)

def iniciar_memebot():
    print("✅ Memebot iniciado com persistência de blacklist.")
    thread = threading.Thread(target=iniciar_monitoramento)
    thread.start()
