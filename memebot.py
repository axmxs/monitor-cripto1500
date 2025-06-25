# === memebot.py ===

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
API_DEXTOOLS = "https://api.dexscreener.com/latest/dex/pairs/bsc"
INTERVALO_MINUTOS = 10
LUCRO_ALVO_1 = 100
LUCRO_ALVO_2 = 200

headers_lunar = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
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

tokens_monitorados = {}

def buscar_tokens_novos():
    try:
        r = requests.get(API_DEXTOOLS)
        data = r.json()
        return data['pairs']
    except:
        return []

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
        if minutos > 180:
            return False
        return True
    except:
        return False

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
                        msg = f"\U0001F4A5 <b>LUCRO +{variacao:.2f}%</b>\n\nToken: {nome}\nVenda sugerida. Preço: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou2"] = True

                    elif variacao >= LUCRO_ALVO_1 and not tokens_monitorados[contrato].get("alertou1"):
                        msg = f"📈 <b>+{variacao:.2f}%</b> em {nome}\nConsidere parcial. Preço: ${preco_atual:.6f}"
                        enviar_mensagem(msg)
                        tokens_monitorados[contrato]["alertou1"] = True

                    elif variacao < -50:
                        msg = f"⚠️ <b>Queda de {variacao:.2f}%</b> em {nome}\nPossível rug. Avalie saída."
                        enviar_mensagem(msg)

                    if datetime.utcnow() - tokens_monitorados[contrato]['ultima_verificacao'] > timedelta(hours=6):
                        del tokens_monitorados[contrato]
        except Exception as e:
            print("Erro ao monitorar token:", e)

        time.sleep(300)

def iniciar_memebot():
    print("🚀 Memebot iniciado.")
    Thread(target=acompanhar_tokens, daemon=True).start()

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

                goplus = verificar_goplus(contrato)
                score = "✅ Token aprovado"
                if goplus.get('result', {}).get(contrato, {}).get('is_open_source') == '0':
                    score = "⚠️ Código fechado"

                social = verificar_social_lunar(nome)
                social_msg = ""
                if social:
                    if social['social_volume'] >= 500 or social['galaxy_score'] >= 60 or social['alt_rank'] <= 25:
                        social_msg = (
                            f"\n\n🔥 Social Volume: {social['social_volume']}\n"
                            f"🧠 Galaxy Score: {social['galaxy_score']}\n"
                            f"📈 Alt Rank: {social['alt_rank']}\n"
                            f"🚀 Muita atenção — tendência viral!"
                        )
                    else:
                        social_msg = f"\n\n📉 Baixo engajamento social no momento."
                else:
                    social_msg = f"\n\n❓ Dados sociais indisponíveis."

                msg = (
                    f"🚨 <b>NOVO ALERTA DE MEME COIN</b>\n\n"
                    f"Token: <b>{nome}</b>\n"
                    f"Market Cap: ${mc:,.0f}\n"
                    f"Liquidez: ${liquidez:,.0f}\n"
                    f"Preço Inicial: ${preco:.6f}\n"
                    f"{score}"
                    f"{social_msg}\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_MINUTOS * 60)

# Se quiser executar diretamente
if __name__ == '__main__':
    iniciar_memebot()
