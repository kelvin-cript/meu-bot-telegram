import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurações de log
logging.basicConfig(level=logging.INFO)

# Inicializa o FastAPI
app = FastAPI()

# Inicializa o Application do python-telegram-bot
application = Application.builder().token("8157218418:AAH6e-anxi5BPvE2pSbJV1QkZk-LqZkeQhY").build()

# Handler para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Eu estou funcionando.")

# Adiciona o handler /start
application.add_handler(CommandHandler("start", start))

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        
        if not data:
            logging.error("Erro JSON inválido: Corpo vazio.")
            return {"ok": False, "error": "Corpo vazio"}

        # Inicializa a aplicação corretamente
        await application.initialize()
        
        # Converte o JSON recebido em um objeto Update
        update = Update.de_json(data, application.bot)
        
        # Processa a atualização (update)
        await application.process_update(update)
        
        # Finaliza a aplicação corretamente
        await application.shutdown()
        
        return {"ok": True}
    
    except ValueError as e:
        logging.error(f"Erro JSON inválido: {e}")
        return {"ok": False, "error": "JSON inválido"}
    
    except Exception as e:
        logging.error(f"Erro ao processar webhook: {e}")
        return {"ok": False, "error": str(e)}

# Roda a aplicação com Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
