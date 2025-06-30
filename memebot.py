import requests
import time
import json
import threading
from datetime import datetime

API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"
INTERVALO_VERIFICACAO = 180  # 3 minutos
blacklist = set()


def buscar_tokens_novos():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        r = requests.get(API_DEXTOOLS, headers=headers, timeout=10)
        print(f"[memebot] Código HTTP: {r.status_code}")  # Mostra status

        # Mostrar parte do conteúdo da resposta
        print(f"[memebot] Conteúdo bruto recebido: {r.text[:500]}")

        if r.status_code != 200:
            print(f"[memebot] Erro HTTP {r.status_code} ao buscar tokens.")
            return []

        try:
            data = r.json()
            print(f"[memebot] JSON recebido da API: {list(data.keys())}")  # Debug
            return data.get("pairs", [])
        except json.JSONDecodeError as e:
            print(f"[memebot] JSON inválido. Erro: {e}")
            return []
    except Exception as e:
        print("[memebot] Erro ao buscar tokens novos:", e)
        return []


def analisar_token(token):
    try:
        nome = token.get("baseToken", {}).get("name")
        simbolo = token.get("baseToken", {}).get("symbol")
        dex = token.get("dexId")
        endereco = token.get("pairAddress")
        liquidez = float(token.get("liquidity", {}).get("usd", 0))
        print(f"[memebot] Analisando token: {simbolo} | Liquidez: {liquidez}")

        if simbolo in blacklist:
            print(f"[memebot] Token {simbolo} já na blacklist. Ignorando.")
            return None

        if liquidez < 10000:  # Ajuste o critério conforme necessário
            print(f"[memebot] Token {simbolo} com baixa liquidez. Ignorando.")
            return None

        url = f"https://dexscreener.com/bsc/{endereco}"
        mensagem = f"🔥 Novo token detectado!\n\nNome: {nome}\nSímbolo: {simbolo}\nDex: {dex}\nLiquidez: ${liquidez:,.2f}\n🔗 {url}"
        return mensagem
    except Exception as e:
        print(f"[memebot] Erro ao analisar token: {e}")
        return None


def enviar_alerta(mensagem):
    print(f"[memebot] Alerta enviado:\n{mensagem}")


def monitorar_tokens():
    while True:
        print(f"[memebot] 🕵️ Verificação iniciada em {datetime.now().strftime('%H:%M:%S')}...")
        tokens = buscar_tokens_novos()
        print(f"[memebot] Tokens recebidos: {len(tokens)}")
        for token in tokens:
            alerta = analisar_token(token)
            if alerta:
                enviar_alerta(alerta)
                simbolo = token.get("baseToken", {}).get("symbol")
                blacklist.add(simbolo)
        print(f"[memebot] Aguardando {INTERVALO_VERIFICACAO} segundos...\n")
        time.sleep(INTERVALO_VERIFICACAO)


def iniciar_memebot():
    print("✅ Memebot iniciado com persistência de blacklist.")
    thread = threading.Thread(target=monitorar_tokens)
    thread.daemon = True
    thread.start()
