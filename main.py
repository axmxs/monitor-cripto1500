import requests

LUNAR_API_KEY = "auwc4pvmbtitld19c8oo92ftmcc08hvtgcdrpil"

headers = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}

url = "https://api.lunarcrush.com/v2?data=assets&symbol=BTC"

try:
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Resposta:", response.json())
except Exception as e:
    print("Erro ao conectar:", e)
