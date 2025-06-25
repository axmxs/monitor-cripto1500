import requests

LUNAR_API_KEY = auwc4pvmbtitld19c8oo92ftmcc08hvtgcdrpil

headers = {
    "Authorization": LUNAR_API_KEY
}

url = "https://api.lunarcrush.com/v4?data=market&key=bitcoin"

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Resposta:", response.json())
