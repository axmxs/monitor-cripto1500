import requests

# Sua chave real da LunarCrush
LUNAR_API_KEY = "auwc4pvmbtitld19c8oo92ftmcc08hvtgcdrpil"

# Cabeçalho correto com Bearer
headers = {
    "Authorization": f"Bearer {LUNAR_API_KEY}"
}

# URL de teste (pegando dados de mercado do Bitcoin, por exemplo)
url = "https://api.lunarcrush.com/v4?data=market&key=bitcoin"

try:
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Resposta:", response.json())
except Exception as e:
    print("Erro ao conectar:", e)
