import asyncio
import random
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from flask import Flask
from threading import Thread
import requests
import os
import time

# Flask para manter o Render ativo
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot está rodando!", 200

def keep_alive():
    """Ping para manter o serviço ativo no Render."""
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        while True:
            try:
                requests.get(url, timeout=10)
                print(f"✅ Ping bem-sucedido para {url}")
            except Exception as e:
                print(f"❌ Erro ao pingar: {e}")
            time.sleep(600)  # Ping a cada 10 minutos

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
        "🚨 SUPER PROMOÇÃO! 🚨", "🔥 OFERTA IMPERDÍVEL! 🔥", "🎉 DESCONTO INCRÍVEL! 🎉",
        "⚡ OFERTA RELÂMPAGO! ⚡", "💥 SUPER DESCONTOOOO! 💥", "🛍️ OFERTA ESPECIAL! 🛍️"
    ]
    return random.choice(promo_headers)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚀 Bem-vindo! Envie o link do produto.")
    context.user_data.clear()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    text = update.message.text.strip()
    
    if "link" not in user_data:
        if "http" in text:
            user_data["link"] = text
            await update.message.reply_text("📌 Agora, envie o título do produto:")
        else:
            await update.message.reply_text("❌ Link inválido. Tente novamente.")
    
    elif "title" not in user_data:
        user_data["title"] = text
        await update.message.reply_text("💲 Qual é o preço original? (Ex: 719,00)")
    
    elif "original_price" not in user_data:
        user_data["original_price"] = text
        await update.message.reply_text("💸 Qual é o preço atual? (Ex: 550,00)")
    
    elif "current_price" not in user_data:
        user_data["current_price"] = text
        keyboard = [[
            InlineKeyboardButton("Normal", callback_data="normal"),
            InlineKeyboardButton("BUG", callback_data="bug")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Escolha o tipo de promoção:", reply_markup=reply_markup)

async def handle_promo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_data = context.user_data
    choice = query.data
    marketplace = extract_marketplace_name(user_data["link"])

    if choice == "normal":
        promo_text = (
            f"{get_promo_header()}\n\n"
            f"🛍️ *{user_data['title']}*\n"
            f"❌ De: ~R$ {user_data['original_price']}~\n"
            f"🔥 Por: *R$ {user_data['current_price']}*\n\n"
            f"🛒 *Promoção {marketplace}!* 🛒\n"
            f"🔗 [Compre aqui]({user_data['link']})\n"
            "_⏳ Promoção por tempo limitado!_"
        )
    elif choice == "bug":
        promo_text = (
            f"🚨 BUG PROMOCIONAL! 🚨\n\n"
            f"🛍️ *{user_data['title']}*\n"
            f"🔥 Preço inacreditável: *R$ {user_data['current_price']}*\n"
            f"🔗 [Clique aqui]({user_data['link']})\n"
            "_⏳ Promoção por tempo limitado!_"
        )

    await query.edit_message_text(promo_text, parse_mode="Markdown")
    user_data.clear()

async def run_bot():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TELEGRAM_TOKEN:
        print("❌ Erro: TELEGRAM_TOKEN não definido.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_promo_choice))
    
    print("🤖 Bot iniciado!")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await app.stop()

def start_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=start_flask).start()
    Thread(target=keep_alive).start()  # Ping contínuo
    asyncio.get_event_loop().create_task(run_bot())  # Inicia bot corretamente
