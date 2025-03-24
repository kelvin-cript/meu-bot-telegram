from fastapi import FastAPI
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

app = FastAPI()  # Cria o serviço FastAPI

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Olá! Envie o link da Shopee ou Mercado Livre para criar o anúncio."
    )

# Manipula mensagens com link
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = update.message.text.strip()
    
    if "shopee" in link.lower():
        context.user_data["link"] = link
        context.user_data["marketplace"] = "Shopee"
        await update.message.reply_text("Por favor, insira a descrição do produto:")
    
    elif "mercadolivre" in link.lower() or "ml." in link.lower():
        context.user_data["link"] = link
        context.user_data["marketplace"] = "Mercado Livre"
        await update.message.reply_text("Por favor, insira a descrição do produto:")
    
    elif "link" in context.user_data:
        descricao = update.message.text.strip()
        link = context.user_data["link"]
        marketplace = context.user_data["marketplace"]
        anuncio = criar_anuncio(link, marketplace, descricao)
        await update.message.reply_text(anuncio, parse_mode="Markdown")
        context.user_data.clear()
    
    else:
        await update.message.reply_text(
            "Por favor, envie um link válido da Shopee ou Mercado Livre."
        )

# Cria o anúncio
def criar_anuncio(link: str, marketplace: str, descricao: str) -> str:
    return (
        f"🚨 *SUPER PROMOÇÃOOO* 🚨\n\n"
        f"{descricao}\n\n"
        f"💸 *De:* R$ \n"
        f"🔥 *Por:* R$ 🥳\n\n"
        f"🛒 *Promoção {marketplace}!*\n\n"
        f"Compre aqui 👉🏻 {link}\n\n"
        "⏳ *Promoção válida por tempo limitado!*"
    )

# Função para iniciar o bot
async def start_bot():
    application = ApplicationBuilder().token("SEU_TOKEN_AQUI").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot iniciado...")
    await application.run_polling()

# Rota HTTP para manter o Render ativo
@app.get("/")
async def root():
    return {"message": "Bot Telegram ativo!"}

# Inicia o bot quando o app FastAPI inicia
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())
