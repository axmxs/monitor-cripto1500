import requests
import os
import time

from dotenv import load_dotenv
load_dotenv()

LUNAR_API_KEY = os.getenv("LUNAR_API_KEY")
GOPLUS_API_KEY = os.getenv("GOPLUS_API_KEY")
SYMBOL = "W"  # símbolo da memecoin a ser analisada

def consultar_lunarcrush(simbolo):
    print(f"📡 Consultando LunarCrush para o ativo: {simbolo}")
    url = f"https://api.lunarcrush.com/v2?data=assets&symbol={simbolo}"
    headers = {
        "Authorization": f"Bearer {LUNAR_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ LunarCrush retornou dados:")
            print(data)
            return data
        else:
            print(f"⚠️ Erro ao acessar LunarCrush. Status code: {response.status_code}")
            print("Resposta:", response.text)
    except Exception as e:
        print("❌ Erro de conexão com LunarCrush:", e)
    return None

def consultar_goplus(token_address, chain="eth"):
    print(f"🔍 Consultando GoPlus Labs para o token: {token_address} na rede {chain}")
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={token_address}"
    headers = {
        "key": GOPLUS_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ GoPlus Labs retornou dados:")
            print(data)
            return data
        else:
            print(f"⚠️ Erro ao acessar GoPlus Labs. Status code: {response.status_code}")
            print("Resposta:", response.text)
    except Exception as e:
        print("❌ Erro de conexão com GoPlus Labs:", e)
    return None

# === INICIAR MEMEBOT ===
def iniciar_memebot():
    print("🚀 Memebot ativo. Iniciando verificações...")
    while True:
        print("\n=== NOVO CICLO MEMEBOT ===")

        # 1. LunarCrush
        dados_lunar = consultar_lunarcrush(SYMBOL)
        if dados_lunar:
            print("📈 LunarCrush OK para:", SYMBOL)
        else:
            print("⚠️ Dados inválidos de LunarCrush.")

        # 2. GoPlus Labs — endereço precisa ser conhecido (exemplo para WORMHOLE)
        endereco_token = "0x08c32b0726cfd34f2d92b8c1d407f0622e0a77f2"
        dados_goplus = consultar_goplus(endereco_token)
        if dados_goplus:
            print("🛡️ GoPlus Labs OK para o token.")
        else:
            print("⚠️ Dados inválidos do GoPlus Labs.")

        # 3. Espera entre os ciclos (pode ajustar o tempo)
        print("🕒 Aguardando 1 hora para nova verificação...\n")
        time.sleep(3600)
