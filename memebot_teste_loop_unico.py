import requests

def main():
    print("🚀 Testando API Dexscreener...")

    url = "https://api.dexscreener.com/latest/dex/pairs/bsc"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        pares = data.get("pairs", [])
        print(f"✅ Total de pares recebidos: {len(pares)}")
        if pares:
            par = pares[0]
            simbolo = par.get("baseToken", {}).get("symbol", "N/A")
            preco = par.get("priceUsd", "N/A")
            print(f"Primeiro par: {simbolo} - Preço: {preco}")
        else:
            print("⚠️ Nenhum par retornado pela API.")
    except Exception as e:
        print("❌ Erro ao consultar API:", e)

if __name__ == "__main__":
    main()
