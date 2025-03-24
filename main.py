@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Lê o corpo da requisição como JSON
        data = await request.json()
        
        # Verifica se o corpo está vazio
        if not data:
            logging.error("Erro JSON inválido: Corpo vazio.")
            return {"ok": False, "error": "Corpo vazio"}
        
        # Inicializa corretamente o Application
        await application.initialize()
        
        # Converte o corpo para Update e processa
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        
        # Finaliza corretamente
        await application.shutdown()
        
        return {"ok": True}

    except ValueError as e:
        logging.error(f"Erro JSON inválido: {e}")
        return {"ok": False, "error": "JSON inválido"}

    except Exception as e:
        logging.error(f"Erro ao processar webhook: {e}")
        return {"ok": False, "error": str(e)}
