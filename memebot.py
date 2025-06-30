import json
from threading import Thread
import time
import requests
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LUNAR_API_KEY = os.getenv("LUNAR_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"
LUCRO_ALVO_1 = 100
LUCRO_ALVO_2 = 200
BLACKLIST_FILE = "blacklist.json"

headers_lunar = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}

tokens_monitorados = {}

# === BLACKLIST persistente ===
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
        resp = requests.post(url, data=payload)
        if resp.status_code != 200:
            print(f"Erro ao enviar mensagem: {resp.status_code} - {resp.text}")
    except Exception as e:
        print("Erro ao enviar:", e)

def verificar_goplus(token_address):
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses={token_address}"
        r = requests.get(url)
        return r.json()
    except Exception as e:
        print("Erro GoPlus Labs:", e)
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
        print("Erro ao consultar LunarCrush:", e)
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
        return r.json().get("pairs", [])
    except:
        return []

def analisar_token(token):
    try:
        if token['chainId'] != 'bsc':
            return False
        if not token.get("baseToken") or not token.get("quoteToken"):
            return False
        if float(token['liquidity']['usd']) < 10000:
            return False
        if float(token['fdv']) > 300000:
            return False
        if float(token['priceUsd']) <= 0:
            return False
        minutos = (datetime.utcnow() - datetime.strptime(token['pairCreatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')).total_seconds() / 60
        if minutos > 30 or minutos < 5:
            return False
        if not verificar_volume_dexscreener(token):
            return False
        if verificar_holders(token['pairAddress']) < 50:
            return False
        return True
    except:
        return False

def acompanhar_tokens():
    while True:
        try:
            print("[memebot] Buscando tokens para monitorar...")
            r = requests.get(API_DEXTOOLS)
            tokens = r.json().get('pairs', [])
            print(f"[memebot] {len(tokens)} tokens recebidos.")

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

                # Atualiza ultima verificação para controle de tempo
                tokens_monitorados[contrato] = tokens_monitorados.get(contrato, {})
                tokens_monitorados[contrato]['ultima_verificacao'] = datetime.utcnow()

                # Remove tokens que não tiveram atualização há mais de 24h
                if datetime.utcnow() - tokens_monitorados[contrato]['ultima_verificacao'] > timedelta(hours=24):
                    tokens_monitorados.pop(contrato, None)

        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(60)

def intervalo_dinamico():
    agora = datetime.now()
    hora_decimal = agora.hour + agora.minute / 60
    return 2 if 6.5 <= hora_decimal <= 21 else 5

def iniciar_memebot():
    print("🚀 Memebot iniciado com persistência de blacklist.")
    enviar_mensagem("✅ Memebot iniciado com sucesso.")
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

        time.sleep(intervalo * 60)

if __name__ == '__main__':
    # Envio teste ao rodar diretamente
    print("🔧 Enviando teste de mensagem...")
    enviar_mensagem("✅ Teste: o bot está funcionando corretamente.")

    print("🔧 Enviando alerta simulado de memecoin...")
    enviar_mensagem(
        "🚨 <b>NOVO ALERTA DE MEME COIN</b>\n\n"
        "Token: <b>TEST123</b>\n"
        "Market Cap: $123,456\n"
        "Liquidez: $45,000\n"
        "Volume 5min: $12,000\n"
        "Volume 24h: $45,000\n"
        "Preço Inicial: $0.000012\n"
        "🔥 Social Volume: 1,200\n"
        "🧠 Galaxy Score: 72.1\n"
        "📈 Alt Rank: 4\n"
        "🔗 <a href='https://dexscreener.com/bsc/0xteste123456789'>Ver Gráfico</a>"
    )

    iniciar_memebot()
