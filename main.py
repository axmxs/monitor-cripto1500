from flask import Flask
from threading import Thread
import time
import requests
import os

# === CONFIG ===
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
INTERVALO_MINUTOS = int(os.environ.get("INTERVALO_MINUTOS", 30))

# === GATILHOS ===
gatilhos = {
    'alta_forte': 40,
    'alta_media': 25,
    'queda_media': -20,
    'queda_forte': -35,
    'lucro_total': 5000,
    'preju_total': -300
}

# === CARTEIRA COM DADOS REAIS ===
ativos = {
    'bittensor': {
        'nome': 'TAO',
        'preco_medio': 2125.7416,
        'quantidade': 0.19757811,
        'custo': 420.00,
        'preco_atual': 1800.10
    },
    'wormhole': {
        'nome': 'W',
        'preco_medio': 0.3587,
        'quantidade': 785.49619314,
        'custo': 281.80,
        'preco_atual': 0.3711
    },
    'arbitrum': {
        'nome': 'ARB',
        'preco_medio': 1.94,
        'quantidade': 115.68959026,
        'custo': 225.00,
        'preco_atual': 1.89
    },
    'hyperliquid': {
        'nome': 'HYPE',
        'preco_medio': 200.0069,
        'quantidade': 0.5821798,
        'custo': 116.44,
        'preco_atual': 215.9194
    },
    'render-token': {
        'nome': 'RNDR',
        'preco_medio': 17.64,
        'quantidade': 6.4060108,
        'custo': 113.00,
        'preco_atual': 17.89
    },
    'pepe': {
        'nome': 'PEPE',
        'preco_medio': 0.00005585,
        'quantidade': 716156.68549906,
        'custo': 40.00,
        'preco_atual': 0.00005684
    },
    'solana': {
        'nome': 'SOL (staking)',
        'preco_medio': 0,
        'quantidade': 0.23164581 + 0.00053688,
        'custo': 0,
        'preco_atual': 196.20
    }
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
        print("Erro ao enviar mensagem:", e)

# === MONITORAMENTO ===
def monitorar():
    while True:
        msg = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0
        ativos_validos = 0

        for id_, d in ativos.items():
            preco = d.get('preco_atual', 0)
            quantidade = d.get('quantidade', 0)
            preco_medio = d.get('preco_medio', 0)

            if preco <= 0 or quantidade <= 0:
                msg.append(f"\n⚠️ {d['nome']} sem dados suficientes.")
                continue

            valor = preco * quantidade
            total_atual += valor
            total_investido += d.get('custo', 0)
            ativos_validos += 1

            if preco_medio > 0:
                variacao_percent = ((preco - preco_medio) / preco_medio) * 100
                linha = f"\n💰 {d['nome']}: R${valor:.2f} ({variacao_percent:+.2f}%)"
                if variacao_percent >= gatilhos['alta_forte']:
                    linha += " 🚨 ALTA FORTE — considerar vender"
                elif variacao_percent >= gatilhos['alta_media']:
                    linha += " 📈 Alta moderada"
                elif variacao_percent <= gatilhos['queda_forte']:
                    linha += " 📉 Queda forte — oportunidade?"
                elif variacao_percent <= gatilhos['queda_media']:
                    linha += " ⚠️ Queda moderada"
            else:
                linha = f"\n💰 {d['nome']}: R${valor:.2f} (staking ou dados incompletos)"

            msg.append(linha)

        if ativos_validos < len(ativos) // 2:
            print("⏸️ Dados insuficientes para envio.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        diferenca = total_atual - total_investido
        if diferenca >= gatilhos['lucro_total']:
            msg.append(f"\n💹 Lucro total R${diferenca:.2f} — ótimo sinal!")
        elif diferenca <= gatilhos['preju_total']:
            msg.append(f"\n🔻 Prejuízo acumulado R${abs(diferenca):.2f}")

        enviar_mensagem("\n".join(msg))
        print("🟢 Alerta enviado com sucesso.")
        time.sleep(INTERVALO_MINUTOS * 60)

# === INÍCIO ===
def iniciar_main():
    print("✅ Main iniciado com sucesso.")
    Thread(target=manter_online).start()
    Thread(target=monitorar).start()

if __name__ == '__main__':
    iniciar_main()
