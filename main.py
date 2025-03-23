import asyncio
import random
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from flask import Flask
from threading import Thread
import requests
import os

# Configuração do Flask para manter o bot ativo no Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot está rodando!", 200

def keep_alive():
    """Evita que o Render desligue o serviço, fazendo pings periódicos."""
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        while True:
            try:
                requests.get(url, timeout=10)
            except Exception as e:
                print(f"Erro ao pingar: {e}")
            asyncio.run(asyncio.sleep(600))  # Pinga a cada 10 minutos

def extract_marketplace_name(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    parts = domain.split('.')
    for part in parts:
        if part not in ["www", "s", "m"]:
            return part.capitalize()
    return "Marketplace"

def get_promo_header() -> str:
    promo_headers = [
        "🚨 SUPER PROMOÇÃOOOOOO 🚨", "🔥 OFERTA IMPERDÍVEL! 🔥", "🎉 DESCONTO INCRÍVEL! 🎉",
        "⚡ OFERTA RELÂMPAGO! ⚡", "💥 SUPER DESCONTOOOO! 💥", "🛍️ OFERTA ESPECIAL! 🛍️", "🔥 OLHAAA ISSOOOO 🔥",
    ]
    return random.choice(promo_headers)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚀 Bem-vindo! Envie o link do produto para começarmos.")
    context.user_data.clear()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    message_text = update.message.text.strip()
    
    if "link" not in user_data:
        if "http" in message_text:
            user_data["link"] = message_text
            await update.message.reply_text("📌 Agora, envie o título do produto:")
        else:
            await update.message.reply_text("❌ Isso não parece um link válido. Tente novamente.")
    elif "title" not in user_data:
        user_data["title"] = message_text
        await update.message.reply_text("💲 Qual é o preço original do produto? (Ex: 719,00)")
    elif "original_price" not in user_data:
        user_data["original_price"] = message_text
        await update.message.reply_text("💸 Qual é o preço atual do produto? (Ex: 550,00)")
    elif "current_price" not in user_data:
        user_data["current_price"] = message_text
        keyboard = [
            [InlineKeyboardButton("Normal", callback_data="normal"), InlineKeyboardButton("BUG", callback_data="bug")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Escolha o tipo de promoção:", reply_markup=reply_markup)

async def handle_promo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    choice = query.data
    
    marketplace_name = extract_marketplace_name(user_data["link"])
    
    if choice == "normal":
        promo_text = (
            f"{get_promo_header()}\n\n"
            f"> 🛍️ *{user_data['title']}*\n\n"
            f"❌ De: ~R$ {user_data['original_price']}~\n"
            f"🔥 Por: *R$ {user_data['current_price']}* 🥳\n\n"
            f"🛒 *Promoção {marketplace_name}!* 🛒\n"
            f"Compre aqui 👉🏻 {user_data['link']}\n\n"
            "_⏳ Promoção válida por tempo limitado!_"
        )
    elif choice == "bug":
        promo_text = (
            f"🚨 SUPER BUGGGGGG 🚨 SÓ *R$ {user_data['current_price']}* 🆘⁉️\n\n"
            f"> 🛍️ {user_data['title']}\n\n"
            "CORREEE ANTES QUE ACABE 😵\n\n"
            f"APROVEITAR LINK PROMOCIONAL 👉🏻 {user_data['link']}\n\n"
            "_⏳ Promoção válida por tempo limitado._"
        )

    await query.edit_message_text(promo_text, parse_mode="Markdown")
    user_data.clear()

async def run_bot():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Pegando token da variável de ambiente
    if not TELEGRAM_TOKEN:
        print("❌ Token do Telegram não encontrado!")
        return
    
    bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    bot.add_handler(CallbackQueryHandler(handle_promo_choice))
    
    print("🤖 Bot iniciado com sucesso!")
    
    await bot.run_polling()  # Start polling

def start_flask():
    port = int(os.environ.get("PORT", 10000))  # Usa porta fornecida pelo Render
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=start_flask).start()
    Thread(target=keep_alive).start()  # Mantém o Render ativo
    asyncio.run(run_bot())
