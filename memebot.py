import requests
import time
import json
import os

# URL da API corrigida (BSC DexScreener)
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"

# Intervalo em minutos para rodar o monitor (3 minutos)
INTERVALO_MINUTOS = 3

BLACKLIST_FILE = "blacklist.json"

def carregar_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            print("[memebot] Erro ao carregar blacklist:", e)
    return set()

def salvar_blacklist(blacklist):
    try:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(list(blacklist), f)
    except Exception as e:
        print("[memebot] Erro ao salvar blacklist:", e)

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
            data = r.json()
            print(f"[memebot] JSON recebido da API: {list(data.keys())}")  # Debug: mostrar chaves do JSON
            return data.get("pairs", [])
        except json.JSONDecodeError:
            print(f"[memebot] Resposta não é JSON válido. Conteúdo: {r.text[:200]}")
            return []
    except Exception as e:
        print("[memebot] Erro ao buscar tokens novos:", e)
        return []

def analisar_token(token):
    # Implementar lógica de análise do token
    # Exemplo básico: verifica se preço está acima de zero e volume razoável
    try:
        price = float(token.get("priceUsd", 0))
        volume = float(token.get("volumeUsd", 0))
        if price > 0 and volume > 1000:  # Critério exemplo
            return True
        return False
    except Exception as e:
        print("[memebot] Erro ao analisar token:", e)
        return False

def iniciar_monitoramento():
    print("[memebot] Thread de monitoramento iniciada.")
    blacklist = carregar_blacklist()

    while True:
        print("[memebot] Buscando tokens para monitorar...")
        tokens = buscar_tokens_novos()
        print(f"[memebot] Tokens recebidos (raw): {tokens}")

        if not tokens:
            print("[memebot] Nenhum token retornado pela API.")
        else:
            print(f"[memebot] {len(tokens)} tokens para analisar.")

        novos = 0
        for token in tokens:
            token_id = token.get("pairAddress")
            if not token_id:
                print("[memebot] Token sem 'pairAddress', ignorando.")
                continue

            if token_id in blacklist:
                print(f"[memebot] Token {token_id} já está na blacklist, ignorando.")
                continue

            if analisar_token(token):
                symbol = token.get("baseToken", {}).get("symbol", "N/D")
                print(f"🟢 Token interessante: {symbol} - {token_id}")
                blacklist.add(token_id)
                novos += 1

        salvar_blacklist(blacklist)

        if novos == 0:
            print("⏸️ Nenhum token novo interessante encontrado.")

        print(f"[memebot] Intervalo de busca: {INTERVALO_MINUTOS} minutos")
        time.sleep(INTERVALO_MINUTOS * 60)

def iniciar_memebot():
    print("✅ Memebot iniciado com persistência de blacklist.")
    iniciar_monitoramento()
