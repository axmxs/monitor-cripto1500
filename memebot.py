import requests
import os
from dotenv import load_dotenv
from main import enviar_mensagem

load_dotenv()

LUNAR_API_KEY = os.getenv("LUNAR_API_KEY")
GOPLUS_API_KEY = os.getenv("GOPLUS_API_KEY")

headers_lunar = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}
headers_goplus = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "API-Key": GOPLUS_API_KEY
}

def testar_lunar():
    url = "https://api.lunarcrush.com/v2?data=assets&symbol=BTC"
    try:
        r = requests.get(url, headers=headers_lunar, timeout=10)
        if r.status_code == 200:
            print("✅ LunarCrush conectado com sucesso!")
            enviar_mensagem("✅ <b>LunarCrush</b> conectado com sucesso!")
        else:
            print(f"❌ LunarCrush falhou ({r.status_code}): {r.text}")
            enviar_mensagem(f"❌ <b>Erro LunarCrush:</b> {r.status_code}")
    except Exception as e:
        print("❌ Erro ao conectar com LunarCrush:", e)
        enviar_mensagem(f"❌ <b>Erro de conexão LunarCrush:</b> {e}")

def testar_goplus():
    url = "https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses=0xdac17f958d2ee523a2206206994597c13d831ec7"
    try:
        r = requests.get(url, headers=headers_goplus, timeout=10)
        if r.status_code == 200:
            print("✅ GoPlus Labs conectado com sucesso!")
            enviar_mensagem("✅ <b>GoPlus Labs</b> conectado com sucesso!")
        else:
            print(f"❌ GoPlus Labs falhou ({r.status_code}): {r.text}")
            enviar_mensagem(f"❌ <b>Erro GoPlus Labs:</b> {r.status_code}")
    except Exception as e:
        print("❌ Erro ao conectar com GoPlus Labs:", e)
        enviar_mensagem(f"❌ <b>Erro de conexão GoPlus:</b> {e}")

def iniciar_memebot():
    print("🚀 Iniciando conexões com LunarCrush e GoPlus Labs...")
    enviar_mensagem("🚀 <b>Iniciando conexões</b> com LunarCrush e GoPlus Labs...")
    testar_lunar()
    testar_goplus()
    print("✅ Memebot finalizou testes de conexão.")
    enviar_mensagem("✅ <b>Memebot</b> terminou os testes de conexão.")
