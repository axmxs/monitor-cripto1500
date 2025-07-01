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
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs"
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
        print("❌ Erro ao salvar blacklist:", e)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=payload)
        print("📤 Status Telegram:", response.status_code, response.text[:100])
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def verificar_goplus(token_address):
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses={token_address}"
        r = requests.get(url)
        return r.json()
    except Exception as e:
        print("❌ Erro GoPlus Labs:", e)
        return {}

def verificar_social_lunar(symbol):
    try:
        url = f"https://api.lunarcrush.com/v2?data=assets&symbol={symbol.upper()}"
        r = requests.get(url, headers=headers_lunar, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if not data:
                return None
            token_data = data[0]
            return {
                "social_volume": token_data.get("social_volume", 0),
                "galaxy_score": token_data.get("galaxy_score", 0),
                "alt_rank": token_data.get("alt_rank", 999)
            }
        return None
    except Exception as e:
        print("❌ Erro ao consultar LunarCrush:", e)
        return None

def verificar_volume_dexscreener(token):
    try:
        vol = token.get("volume", {})
        vol_m5 = float(vol.get("m5", 0))
        vol_h24 = float(vol.get("h24", 0))
        return vol_m5 >= 3000 and vol_h24 >= 10000
    except:
        return False

def verificar_holders(token_address):
    try:
        url = f"https://api.bscscan.com/api?module=token&action=tokenholderlist&contractaddress={token_address}&page=1&offset=100&apikey={BSCSCAN_API_KEY}"
        r = requests.get(url)
        data = r.json()
        if 'result' in data:
            return len(data['result'])
    except:
        pass
    return 0

def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        pares = r.json().get("pairs", [])
        return [t for t in pares if t.get("chainId") == "bsc"]
    except Exception as e:
        print("❌ Erro ao buscar tokens novos:", e)
        return []

def analisar_token(token):
    try:
        if not token.get("baseToken") or not token.get("quoteToken"):
            print("⛔ Token sem base/quote")
            return False
        if float(token['liquidity']['usd']) < 10000:
            print(f"⛔ Liquidez baixa: {token['baseToken']['symbol']}")
            return False
        if float(token['fdv']) > 300000:
            print(f"⛔ FDV muito alta: {token['baseToken']['symbol']}")
            return False
        if float(token['priceUsd']) <= 0:
            print(f"⛔ Preço inválido: {token['baseToken']['symbol']}")
            return False
        minutos = (datetime.utcnow() - datetime.strptime(token['pairCreatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() / 60
        if minutos > 30 or minutos < 5:
            print(f"⛔ Tempo de vida fora do intervalo: {token['baseToken']['symbol']} ({minutos:.1f} min)")
            return False
        if not verificar_volume_dexscreener(token):
            print(f"⛔ Volume insuficiente: {token['baseToken']['symbol']}")
            return False
        holders = verificar_holders(token['pairAddress'])
        if holders < 50:
            print(f"⛔ Poucos holders: {token['baseToken']['symbol']} ({holders})")
            return False
        return True
    except Exception as e:
        print("❌ Erro ao analisar token:", e)
        return False

def intervalo_dinamico():
    agora = datetime.now()
    hora_decimal = agora.hour + agora.minute / 60
    return 2 if 6.5 <= hora_decimal <= 21 else 5

def iniciar_memebot():
    print("🚀 Memebot iniciado com debug")
    enviar_mensagem("🧪 <b>DEBUG</b>: Memebot rodando com sucesso!")

    while True:
        print(f"\n🔁 Loop iniciado às {datetime.utcnow().strftime('%H:%M:%S')}")

        tokens = buscar_tokens_novos()
        print(f"📊 {len(tokens)} tokens encontrados na BSC")

        for token in tokens:
            contrato = token['pairAddress']
            nome = token['baseToken']['symbol']

            if contrato in blacklist_tokens or contrato in tokens_monitorados:
                continue

            if not analisar_token(token):
                print(f"🔒 {nome} rejeitado — não passou nos filtros")
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            goplus = verificar_goplus(contrato)
            if goplus.get('result', {}).get(contrato, {}).get('is_open_source') == '0':
                print(f"🛑 {nome} rejeitado pelo GoPlus (não open source)")
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            social = verificar_social_lunar(nome)
            if not social:
                print(f"📉 {nome} rejeitado — sem dados sociais")
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue
            if social['social_volume'] < 500 or social['alt_rank'] > 25:
                print(f"📉 {nome} rejeitado por social: vol={social['social_volume']} alt_rank={social['alt_rank']}")
                blacklist_tokens.add(contrato)
                salvar_blacklist()
                continue

            preco = float(token['priceUsd'])
            mc = float(token.get('fdv', 0))
            liquidez = float(token['liquidity']['usd'])

            tokens_monitorados[contrato] = {
                "preco_inicial": preco,
                "ultima_verificacao": datetime.utcnow(),
                "alertou1": False,
                "alertou2": False,
            }

            print(f"✅ Token ACEITO: {nome} — enviando alerta")

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

        intervalo = intervalo_dinamico()
        print(f"⏳ Aguardando {intervalo} minutos para o próximo loop...\n")
        time.sleep(intervalo * 60)

if __name__ == '__main__':
    iniciar_memebot()
