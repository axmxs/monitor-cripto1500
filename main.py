import os
import requests

# === NOVO BLOCO: API Mercado Bitcoin ===

MB_API_KEY = os.environ.get("MB_API_KEY")
MB_API_SECRET = os.environ.get("MB_API_SECRET")  # Pode ser necessário para HMAC
MB_API_BASE = "https://www.mercadobitcoin.net/api"

def obter_carteira_mercado_bitcoin():
    # ⚠️ Isso é um esqueleto. Para autenticação real, você deve usar HMAC + Nonce + assinatura.
    headers = {
        'Authorization': f'Bearer {MB_API_KEY}'
    }
    try:
        r = requests.get(f"{MB_API_BASE}/v4/accounts/balance", headers=headers)
        r.raise_for_status()
        data = r.json()
        
        # Filtra apenas criptos com saldo disponível > 0
        ativos = {}
        for simbolo, valores in data['balances'].items():
            saldo = float(valores.get('available', 0))
            if saldo > 0:
                ativos[simbolo.lower()] = {
                    'nome': simbolo.upper(),
                    'quantidade': saldo,
                    'preco_medio': 0.0,  # Esse dado você precisará calcular ou importar manualmente
                    'custo': 0.0,
                    'preco_atual': 0.0  # Será preenchido depois via CoinGecko ou outra API
                }
        return ativos
    except Exception as e:
        print(f"❌ Erro ao obter carteira do Mercado Bitcoin: {e}")
        return {}