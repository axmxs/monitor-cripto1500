# === COINGECKO COM RECONEXÃO ===
def precos_reais(tentativas=3, espera=2):
    ids = ','.join(ativos.keys())
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=brl'
    print(f"🔍 Consultando API CoinGecko com os ativos: {ids}")

    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            if data:
                print("✅ Dados recebidos da API CoinGecko:", data)
                return data
            else:
                print("⚠️ Resposta vazia da API.")
        except Exception as e:
            print(f"❌ Tentativa {i+1} falhou: {e}")
        time.sleep(espera)
    return {}

# === MONITORAMENTO ===
def monitorar():
    while True:
        print("⏱️ Iniciando novo ciclo de monitoramento...")
        dados = precos_reais()
        if not dados:
            print("⏸️ Nenhum dado de preço foi retornado, aguardando o próximo ciclo.")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        msg = ["<b>📊 AlertaCripto1500</b>"]
        total_atual = total_investido = 0
        ativos_validos = 0

        for id_, d in ativos.items():
            preco = dados.get(id_, {}).get('brl', 0)
            if preco <= 0:
                msg.append(f"\n⚠️ {d['nome']} sem preço disponível.")
                print(f"⚠️ {d['nome']} — preço indisponível.")
                continue

            ativos_validos += 1
            valor = preco * d['quantidade']
            total_atual += valor
            total_investido += d['compra']
            variacao = (valor - d['compra']) / d['compra'] * 100

            linha = f"\n💰 {d['nome']}: R${valor:.2f} ({variacao:+.2f}%)"
            if variacao >= gatilhos['alta_forte']:
                linha += " 🚨 ALTA FORTE — considerar vender"
            elif variacao >= gatilhos['alta_media']:
                linha += " 📈 Alta moderada"
            elif variacao <= gatilhos['queda_forte']:
                linha += " 📉 Queda forte — oportunidade?"
            elif variacao <= gatilhos['queda_media']:
                linha += " ⚠️ Queda moderada"
            msg.append(linha)

        if ativos_validos < len(ativos) // 2:
            print("⏸️ Dados insuficientes para envio (ativos com preço válido insuficiente).")
            time.sleep(INTERVALO_MINUTOS * 60)
            continue

        dif = total_atual - total_investido
        if dif >= gatilhos['lucro_total']:
            msg.append(f"\n💹 Lucro total R${dif:.2f} — ótimo sinal!")
        elif dif <= gatilhos['preju_total']:
            msg.append(f"\n🔻 Prejuízo acumulado R${abs(dif):.2f}")

        print("📤 Enviando alerta para o Telegram...")
        enviar_mensagem("\n".join(msg))
        print("✅ Alerta enviado com sucesso!")
        print("🔁 Aguardando o próximo ciclo...")
        time.sleep(INTERVALO_MINUTOS * 60)
