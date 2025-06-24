def iniciar_memebot():
    print("🚀 Memebot iniciado.")
    threading.Thread(target=acompanhar_tokens, daemon=True).start()

    while True:
        tokens = buscar_tokens_novos()
        for token in tokens:
            if not analisar_token(token):
                continue

            contrato = token['pairAddress']
            nome = token['baseToken']['symbol']
            preco = float(token['priceUsd'])
            mc = float(token.get('fdv', 0))
            liquidez = float(token['liquidity']['usd'])
            holders = token.get("holders", "?")

            if contrato not in tokens_monitorados:
                tokens_monitorados[contrato] = {
                    "preco_inicial": preco,
                    "ultima_verificacao": datetime.utcnow(),
                }

                msg = (
                    f"🚨 <b>NOVO ALERTA DE MEME COIN</b>\n\n"
                    f"Token: <b>{nome}</b>\n"
                    f"Market Cap: ${mc:,.0f}\n"
                    f"Liquidez: ${liquidez:,.0f}\n"
                    f"Preço Inicial: ${preco:.6f}\n"
                    f"🧠 Detecção de possível pump (nas próximas horas).\n\n"
                    f"🔗 <a href='https://dexscreener.com/bsc/{contrato}'>Ver Gráfico</a>"
                )
                enviar_mensagem(msg)

        time.sleep(INTERVALO_ANALISE)
