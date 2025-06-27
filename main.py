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
INTERVALO_MINUTOS = 30

# === GATILHOS ===
gatilhos = {
    'alta_forte': 40,
    'alta_media': 25,
    'queda_media': -20,
    'queda_forte': -35,
    'lucro_total': 5000,
    'preju_total': -300
}

# === CARTEIRA ===
ativos = {
    'bittensor': {'nome': 'TAO', 'compra': 420.00, 'quantidade': 0.19757811},
    'wormhole': {'nome': 'W', 'compra': 281.80, 'quantidade': 785.49619314},
    'arbitrum': {'nome': 'ARB', 'compra': 225.00, 'quantidade': 115.68959026},
    'hyperliquid': {'nome': 'HYPE', 'compra': 116.44, 'quantidade': 0.5821798},
    'render-token': {'nome': 'RNDR', 'compra': 113.00, 'quantidade': 6.4060108},
    'pepe': {'nome': 'PEPE', 'compra': 40.00, 'quantidade': 716156.68549906}
}

# === FLASK PARA RENDER/UPTIME ROBOT ===
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot monitorando sua carteira cripto com sucesso!'

def manter_online():
    app.run(host='0.0.0.0', port=3000)

# === TELEGRAM ===
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': texto, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar:", e)

# === COINGECKO COM RECONEXÃO ===
def precos_reais(tentativas=3, espera=2):
    ids = ','.join(ativos.keys())
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=brl'
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            if data:
                return data
        except Exception as e:
            print(f"Tentativa {i+1} falhou: {e}")
        time.sleep(espera)
    return {}

# === MONITORAMENTO ===
def monitorar():
    while True:
        dados = precos_reais()
        if not dados:
            print("⏸️ Nenhum dado de preço foi retornado, aguardando o próximo ciclo.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        msg = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0
        ativos_validos = 0

        for id_, d in ativos.items():
            preco = dados.get(id_, {}).get('brl', 0)
            if preco <= 0:
                msg.append(f"\n⚠️ {d['nome']} sem preço disponível.")
                continue

            ativos_validos += 1
            preco_medio_unitario = d['compra'] / d['quantidade']
            variacao = (preco - preco_medio_unitario) / preco_medio_unitario * 100

            valor = preco * d['quantidade']
            total_atual += valor
            total_investido += d['compra']

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

        if ativos_validos < len(ativos) // 2:
            print("⏸️ Dados insuficientes para envio (ativos com preço válido insuficiente).")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        dif = total_atual - total_investido
        if dif >= gatilhos['lucro_total']:
            msg.append(f"\n💹 Lucro total R${dif:.2f} — ótimo sinal!")
        elif dif <= gatilhos['preju_total']:
            msg.append(f"\n🔻 Prejuízo acumulado R${abs(dif):.2f}")

        enviar_mensagem("\n".join(msg))
        print("🟢 Alerta enviado. Nova verificação em breve...")
        time.sleep(INTERVALO_MINUTOS * 60)

# === FUNÇÃO DE INÍCIO PARA IMPORTAÇÃO EXTERNA ===
def iniciar_main():
    print("✅ Main iniciado com sucesso.")
    Thread(target=manter_online).start()
    Thread(target=monitorar).start()

# Execução direta
if __name__ == '__main__':
    iniciar_main()
