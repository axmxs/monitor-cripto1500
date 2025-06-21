from flask import Flask
from threading import Thread
import time
import requests
import os
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO_MINUTOS = 60

# === GATILHOS ===
gatilhos = {
    'alta_forte': 40,
    'alta_media': 25,
    'queda_media': -20,
    'queda_forte': -35,
    'lucro_total': 5000,
    'preju_total': -300
}

# === CARTEIRA ATUALIZADA ===
ativos = {
    'bittensor': {'nome': 'TAO', 'compra': 416.80, 'quantidade': 0.1975781},
    'wormhole': {'nome': 'W', 'compra': 281.97, 'quantidade': 785.49619314},
    'arbitrum': {'nome': 'ARB', 'compra': 225.00, 'quantidade': 115.68959026},
    'solana': {'nome': 'SOL', 'compra': 183.54, 'quantidade': 0.23164581},
    'hyperliquid': {'nome': 'HYPE', 'compra': 110.90, 'quantidade': 0.5821798},
    'render-token': {'nome': 'RNDR', 'compra': 106.69, 'quantidade': 6.40601079},
    'pepe': {'nome': 'PEPE', 'compra': 38.53, 'quantidade': 716156.68549905},
}

# === FLASK PARA UPTIMEROBOT ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitorando sua carteira cripto com sucesso!'

def manter_online():
    app.run(host='0.0.0.0', port=3000)

# === ENVIA MENSAGEM TELEGRAM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === PREÇOS ===
def precos_reais():
    ids = ','.join(ativos.keys())
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=brl'
    try:
        return requests.get(url).json()
    except:
        return {}

# === LOOP PRINCIPAL ===
def monitorar():
    while True:
        dados = precos_reais()
        msg = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0

        for id_, d in ativos.items():
            preco = dados.get(id_, {}).get('brl', 0)
            if preco <= 0:
                msg.append(f"\n⚠️ {d['nome']} sem preço disponível.")
                continue

            valor = preco * d['quantidade']
            total_atual += valor
            total_investido += d['compra']
            variacao = (valor - d['compra']) / d['compra'] * 100

            linha = f"\n💰 {d['nome']}: R${valor:.2f} ({variacao:+.2f}%)"
            if variacao >= gatilhos['alta_forte']:
                linha += " 🚨 ALTA FORTE — considerar vender"
            elif variacao >= gatilhos['alta_media']:
                linha += " 📈 Alta moderada"
            elif variacao <= gatilhos['queda_forte']:
                linha += " 📉 Queda forte — oportunidade?"
            elif variacao <= gatilhos['queda_media']:
                linha += " ⚠️ Queda moderada"
            msg.append(linha)

        dif = total_atual - total_investido
        if dif >= gatilhos['lucro_total']:
            msg.append(f"\n💹 Lucro total R${dif:.2f} — ótimo sinal!")
        elif dif <= gatilhos['preju_total']:
            msg.append(f"\n🔻 Prejuízo acumulado R${abs(dif):.2f}")

        enviar_mensagem("\n".join(msg))
        print("🟢 Alerta enviado. Nova verificação em breve...")
        time.sleep(INTERVALO_MINUTOS * 60)

# === START ===
if __name__ == '__main__':
    Thread(target=manter_online).start()
    monitorar()
