import nest_asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI, Request
import uvicorn

# Aplicação assíncrona Nest AsyncIO
nest_asyncio.apply()

# Configuração de logs
logging.basicConfig(level=logging.INFO)

# Inicializa FastAPI
app = FastAPI()

# Token do bot (mantenha-o seguro)
TOKEN = "8157218418:AAH6e-anxi5BPvE2pSbJV1QkZk-LqZkeQhY"

# Cria aplicação Telegram
application = Application.builder().token(TOKEN).build()

# Handler para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Envie o link da Shopee ou Mercado Livre para criar o anúncio.")

# Handler para mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = update.message.text.strip()
    
    if "shopee" in link.lower():
        context.user_data["link"] = link
        context.user_data["marketplace"] = "Shopee"
        await update.message.reply_text("Por favor, insira a descrição do produto.")
    
    elif "mercadolivre" in link.lower() or "ml." in link.lower():
        context.user_data["link"] = link
        context.user_data["marketplace"] = "Mercado Livre"
        await update.message.reply_text("Por favor, insira a descrição do produto.")
    
    elif "link" in context.user_data:
        descricao = update.message.text.strip()
        link = context.user_data["link"]
        marketplace = context.user_data["marketplace"]
        anuncio = criar_anuncio(link, marketplace, descricao)
        await update.message.reply_text(anuncio, parse_mode="Markdown")
        context.user_data.clear()
    
    else:
        await update.message.reply_text("Por favor, envie um link válido.")

# Cria o anúncio formatado
def criar_anuncio(link: str, marketplace: str, descricao: str) -> str:
    return (
        f"🚨 *SUPER PROMOÇÃO!* 🚨\n"
        f"{descricao}\n\n"
        f"🛒 [Compre aqui]({link})\n"
        "⏳ Promoção por tempo limitado!"
    )

# Registra handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Rota root
@app.get("/")
async def root():
    return {"status": "Bot rodando no Render!"}

# Webhook com inicialização correta
@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Inicializa o Application corretamente
        await application.initialize()
        
        data = await request.json()
        update = Update.de_json(data, application.bot)
        
        # Processa a atualização
        await application.process_update(update)
        
        # Finaliza corretamente após processar
        await application.shutdown()
        
        return {"ok": True}
    
    except ValueError as e:  # Erro JSON inválido
        logging.error(f"Erro JSON inválido: {e}")
        return {"ok": False, "error": "JSON inválido"}
    
    except Exception as e:
        logging.error(f"Erro ao processar webhook: {e}")
        return {"ok": False, "error": str(e)}

# Inicia FastAPI com Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
