import requests

def testar_dexscreener():
    url = "https://api.dexscreener.com/latest/dex/pairs/bsc"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Dados recebidos da API Dexscreener (exemplo parcial):")
            # Mostrar os primeiros 3 pares para evitar muito output
            pares = data.get("pairs", [])
            print(f"Total de pares recebidos: {len(pares)}")
            for i, par in enumerate(pares[:3]):
                print(f"Par {i+1}:")
                print(par)
        else:
            print("Erro na resposta da API:", response.text)
    except Exception as e:
        print("Erro na requisição:", e)

if __name__ == "__main__":
    testar_dexscreener()
