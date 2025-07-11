import os
import time
import requests
from threading import Thread
from flask import Flask

# === CONFIGURAÇÕES ===
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MB_API_KEY = os.getenv("MB_API_KEY")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 30))

# === GATILHOS PARA ALERTAS ===
gatilhos = {
    'alta_forte': 40,
    'alta_media': 25,
    'queda_media': -20,
    'queda_forte': -35,
    'lucro_total': 5000,
    'preju_total': -300
}

# === FLASK (Render / UptimeRobot) ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitorando carteira do Mercado Bitcoin com sucesso!'

def manter_online():
    app.run(host='0.0.0.0', port=3000)

# === TELEGRAM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# === PREÇO EM TEMPO REAL ===
def preco_em_reais_coin_gecko(cripto_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cripto_id}&vs_currencies=brl"
        r = requests.get(url)
        return r.json()[cripto_id]['brl']
    except Exception as e:
        print(f"Erro ao buscar preço de {cripto_id}: {e}")
        return 0

# === MAPA DE IDs PARA COINGECKO ===
mapa_coingecko = {
    "tao": "bittensor",
    "w": "wormhole",
    "arb": "arbitrum",
    "hype": "hyperliquid",
    "rndr": "render-token",
    "pepe": "pepe",
    "sol": "solana"
}

# === CARTEIRA DO MERCADO BITCOIN ===
def obter_carteira_mercado_bitcoin():
    url = "https://api.mercadobitcoin.net/api/v4/accounts/balance"
    headers = {'Authorization': f'Bearer {MB_API_KEY}'}
    ativos = {}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

        for simbolo, info in data['balances'].items():
            quantidade = float(info.get("available", 0))
            if quantidade > 0:
                ativos[simbolo.lower()] = {
                    'nome': simbolo.upper(),
                    'quantidade': quantidade,
                    'preco_medio': 0,  # manualmente por enquanto
                    'custo': 0,        # manualmente por enquanto
                    'preco_atual': 0
                }
        return ativos
    except Exception as e:
        print(f"Erro ao buscar carteira MB: {e}")
        return {}

# === MONITORAMENTO ===
def monitorar():
    while True:
        ativos = obter_carteira_mercado_bitcoin()
        if not ativos:
            print("❌ Nenhum ativo encontrado.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        msg = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0

        for simbolo, d in ativos.items():
            id_cg = mapa_coingecko.get(simbolo)
            if not id_cg:
                msg.append(f"\n⚠️ {d['nome']}: sem CoinGecko ID.")
                continue

            preco = preco_em_reais_coin_gecko(id_cg)
            quantidade = d['quantidade']
            preco_medio = d['preco_medio']
            custo = d['custo']

            valor = preco * quantidade
            total_atual += valor
            total_investido += custo
            d['preco_atual'] = preco

            if preco_medio > 0:
                variacao_percent = ((preco - preco_medio) / preco_medio) * 100
                linha = f"\n💰 {d['nome']}: R${valor:.2f} ({variacao_percent:+.2f}%)"
                if variacao_percent >= gatilhos['alta_forte']:
                    linha += " 🚨 ALTA FORTE"
                elif variacao_percent >= gatilhos['alta_media']:
                    linha += " 📈 Alta moderada"
                elif variacao_percent <= gatilhos['queda_forte']:
                    linha += " 📉 Queda forte"
                elif variacao_percent <= gatilhos['queda_media']:
                    linha += " ⚠️ Queda moderada"
            else:
                linha = f"\n💰 {d['nome']}: R${valor:.2f} (sem preço médio)"

            msg.append(linha)

        diferenca = total_atual - total_investido
        if diferenca >= gatilhos['lucro_total']:
            msg.append(f"\n💹 Lucro total R${diferenca:.2f}")
        elif diferenca <= gatilhos['preju_total']:
            msg.append(f"\n🔻 Prejuízo acumulado R${abs(diferenca):.2f}")

        enviar_mensagem("\n".join(msg))
        print("✅ Alerta enviado.")
        time.sleep(INTERVALO_MINUTOS * 60)

# === INICIAR BOT ===
def iniciar_main():
    print("✅ Bot iniciado com sucesso.")
    Thread(target=manter_online).start()
    Thread(target=monitorar).start()

if __name__ == '__main__':
    iniciar_main()