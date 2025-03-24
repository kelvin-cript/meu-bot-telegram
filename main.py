import nest_asyncio
import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

# Aplicando nest_asyncio para evitar conflitos no loop de eventos
nest_asyncio.apply()

# Criando a aplicação FastAPI
app = FastAPI()

# Obtendo o token do bot das variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Verifica se o token foi encontrado
if not TELEGRAM_TOKEN:
    raise ValueError("O token do bot do Telegram não foi encontrado. Defina a variável TELEGRAM_TOKEN no Render.")

# Função /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Envie o link da Shopee ou Mercado Livre para criar o anúncio.")

# Manipulador de mensagens
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
        await update.message.reply_text("Por favor, envie um link válido da Shopee ou Mercado Livre.")

# Função para criar o anúncio
def criar_anuncio(link: str, marketplace: str, descricao: str) -> str:
    return (
        f"🚨 *SUPER PROMOÇÃOOO* 🚨\n"
        f"{descricao}\n\n"
        f"💸 *De:* R$ \n"
        f"🔥 *Por:* R$ 🥳\n\n"
        f"🛒 *Promoção {marketplace}!*\n\n"
        f"Compre aqui 👉🏻 {link}\n\n"
        "⏳ *Promoção válida por tempo limitado!*"
    )

# Inicializando o bot do Telegram
async def start_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot iniciado...")
    await application.run_polling()

# Rota para verificar o status do bot no Render
@app.get("/")
async def home():
    return {"status": "Bot rodando no Render!"}

# Iniciando o bot de forma assíncrona
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    loop.run_forever()
