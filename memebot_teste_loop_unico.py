import requests

url = "https://api.dexscreener.com/latest/dex/pairs"
try:
    response = requests.get(url, timeout=10)
    print("Status:", response.status_code)
    data = response.json()
    print("Exemplo de par:", data['pairs'][0] if 'pairs' in data else "Nenhum par retornado.")
except Exception as e:
    print("Erro ao acessar a API:", e)
