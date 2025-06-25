# memebot_v2.py (parte 1/3): Análise de Honeypot + Risco do Contrato (GoPlus)

import requests

def verificar_honeypot(contract_address):
    try:
        url = f"https://api.honeypot.is/v1/contract/bsc/{contract_address}"
        response = requests.get(url)
        data = response.json()

        if data.get("honeypotResult", {}).get("isHoneypot"):
            return False, "🚫 Honeypot detectado!"
        return True, "✅ Sem honeypot"
    except:
        return True, "❓ Não foi possível verificar honeypot"

def verificar_risco_goplus(contract_address):
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses={contract_address}"
        r = requests.get(url)
        data = r.json()

        info = data.get("result", {}).get(contract_address.lower(), {})
        riscos = []

        if info.get("is_open_source") == "0":
            riscos.append("Contrato fechado")
        if info.get("can_take_back_ownership") == "1":
            riscos.append("Dono pode retomar controle")
        if info.get("slippage_modifiable") == "1":
            riscos.append("Taxa pode ser alterada")
        if info.get("is_blacklisted") == "1":
            riscos.append("Token tem blacklist")
        if info.get("owner_change_balance") == "1":
            riscos.append("Owner pode alterar saldo")

        risco_detectado = len(riscos) > 0
        return not risco_detectado, riscos if risco_detectado else ["Sem riscos graves"]

    except Exception as e:
        return True, ["Erro ao verificar contrato"]
