# main.py

import os
import time
import requests
import logging
from threading import Thread
from flask import Flask

# === CONFIGURAÇÃO DE LOG ===
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# === VARIÁVEIS DE AMBIENTE ===
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 30))

# === GATILHOS ===
gatilhos = {
    "alta_forte": 40,
    "alta_media": 25,
    "queda_media": -20,
    "queda_forte": -35,
    "lucro_total": 5000,
    "preju_total": -300
}

# === CARTEIRA ===
ativos = {
    "bittensor":    {"nome": "TAO",  "compra": 420.00, "quantidade": 0.19757811},
    "wormhole":     {"nome": "W",    "compra": 281.80, "quantidade": 785.49619314},
    "arbitrum":     {"nome": "ARB",  "compra": 225.00, "quantidade": 115.68959026},
    "hyperliquid":  {"nome": "HYPE", "compra": 116.44, "quantidade": 0.5821798},
    "render-token": {"nome": "RNDR", "compra": 113.00, "quantidade": 6.4060108},
    "pepe":         {"nome": "PEPE", "compra": 40.00,  "quantidade": 716156.68549906}
}

# === FLASK PARA UPTIME ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot monitorando sua carteira cripto com sucesso!"

def manter_online():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))

# === TELEGRAM ===
def enviar_mensagem(texto: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        logging.info("Mensagem enviada ao Telegram")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem: {e}")

# === PREÇOS COM RECONEXÃO ===
def precos_reais(tentativas=3, espera=2):
    ids = ",".join(ativos.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=brl"
    for i in range(1, tentativas+1):
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            if data:
                return data
        except Exception as e:
            logging.warning(f"Tentativa {i} falhou: {e}")
            time.sleep(espera)
    return {}

# === MONITORAMENTO ===
def monitorar():
    while True:
        dados = precos_reais()
        if not dados:
            logging.warning("⏸️ Sem dados de preço; próximo ciclo em breve.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        linhas = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0
        validos = 0

        for id_, d in ativos.items():
            preco = dados.get(id_, {}).get("brl", 0)
            if preco <= 0:
                linhas.append(f"\n⚠️ {d['nome']} sem preço disponível.")
                continue

            validos += 1
            preco_medio = d["compra"]
            variacao = (preco - preco_medio) / preco_medio * 100
            valor = preco * d["quantidade"]
            total_atual += valor
            total_investido += preco_medio * d["quantidade"]

            tag = ""
            if variacao >= gatilhos["alta_forte"]:
                tag = " 🚨 ALTA FORTE — considerar vender"
            elif variacao >= gatilhos["alta_media"]:
                tag = " 📈 Alta moderada"
            elif variacao <= gatilhos["queda_forte"]:
                tag = " 📉 Queda forte — oportunidade?"
            elif variacao <= gatilhos["queda_media"]:
                tag = " ⚠️ Queda moderada"

            linhas.append(f"\n💰 {d['nome']}: R${valor:.2f} ({variacao:+.2f}%){tag}")

        if validos < len(ativos) // 2:
            logging.warning("⏸️ Ativos válidos abaixo do mínimo; aguardando.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        dif = total_atual - total_investido
        if dif >= gatilhos["lucro_total"]:
            linhas.append(f"\n💹 Lucro total R${dif:.2f} — ótimo sinal!")
        elif dif <= gatilhos["preju_total"]:
            linhas.append(f"\n🔻 Prejuízo total R${abs(dif):.2f}")

        enviar_mensagem("\n".join(linhas))
        logging.info("🟢 Alerta enviado; próximo em breve.")
        time.sleep(INTERVALO_MINUTOS * 60)

# === INICIALIZAÇÃO ===
def iniciar_main():
    logging.info("✅ Main iniciado com sucesso.")
    Thread(target=manter_online, daemon=True).start()
    Thread(target=monitorar, daemon=True).start()

if __name__ == "__main__":
    iniciar_main()
