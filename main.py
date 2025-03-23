import asyncio
import random
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

def extract_marketplace_name(url: str) -> str:
    """
    Extrai corretamente o nome do marketplace a partir do link.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    parts = domain.split('.')
    for part in parts:
        if part not in ["www", "s", "m"]:
            return part.capitalize()  # Retorna o nome capitalizado

    return "Marketplace"

def get_promo_header() -> str:
    """
    Retorna uma variação aleatória do cabeçalho de promoção.
    """
    promo_headers = [
        "🚨 SUPER PROMOÇÃOOOOOO 🚨",
        "🔥 OFERTA IMPERDÍVEL! 🔥",
        "🎉 DESCONTO INCRÍVEL! 🎉",
        "⚡ OFERTA RELÂMPAGO! ⚡",
        "💥 SUPER DESCONTOOOO! 💥",
        "🛍️ OFERTA ESPECIAL! 🛍️",
        "🔥 OLHAAA ISSOOOO 🔥",
    ]
    return random.choice(promo_headers)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚀 Bem-vindo! Envie o link do produto para começarmos.")
    context.user_data.clear()  # Limpa dados anteriores

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    message_text = update.message.text.strip()

    # Etapa 1: Receber o link
    if "link" not in user_data:
        if "http" in message_text:
            user_data["link"] = message_text
            await update.message.reply_text("📌 Agora, envie o título do produto:")
        else:
            await update.message.reply_text("❌ Isso não parece um link válido. Tente novamente.")
    
    # Etapa 2: Receber o título
    elif "title" not in user_data:
        user_data["title"] = message_text
        await update.message.reply_text("💲 Qual é o preço original do produto? (Ex: 719,00)")

    # Etapa 3: Receber o preço original
    elif "original_price" not in user_data:
        user_data["original_price"] = message_text
        await update.message.reply_text("💸 Qual é o preço atual do produto? (Ex: 550,00)")

    # Etapa 4: Receber o preço atual
    elif "current_price" not in user_data:
        user_data["current_price"] = message_text
        
        # Pergunta se é "normal" ou "BUG"
        keyboard = [
            [
                InlineKeyboardButton("Normal", callback_data="normal"),
                InlineKeyboardButton("BUG", callback_data="bug"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Escolha o tipo de promoção:", reply_markup=reply_markup)

async def handle_promo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    choice = query.data  # "normal" ou "bug"
    
    marketplace_name = extract_marketplace_name(user_data["link"])

    if choice == "normal":
        promo_header = get_promo_header()
        promo_text = (
            f"{promo_header}\n\n"
            f"> 🛍️ *{user_data['title']}*\n\n"
            f"❌ De: ~R$ {user_data['original_price']}~\n"
            f"🔥 Por: *R$ {user_data['current_price']}* 🥳\n\n"
            f"🛒 *Promoção {marketplace_name}!* 🛒\n"
            f"Compre aqui 👉🏻 {user_data['link']}\n\n"
            "_⏳ Promoção válida por tempo limitado!_"
        )
    elif choice == "bug":
        promo_text = (
            "🚨 SUPER BUGGGGGG 🚨 SÓ *R$ {current_price}* 🆘⁉️\n\n"
            f"> 🛍️ {user_data['title']}\n\n"
            "CORREEE ANTES QUE ACABE 😵\n\n"
            "APROVEITAR LINK PROMOCIONAL 👉🏻\n"
            f"{user_data['link']}\n\n"
            "_⏳ Promoção válida por tempo limitado._"
        ).format(current_price=user_data['current_price'])

    await query.edit_message_text(promo_text, parse_mode="Markdown")
    user_data.clear()  # Limpa dados após envio

async def main() -> None:
    TELEGRAM_TOKEN = "8157218418:AAH6e-anxi5BPvE2pSbJV1QkZk-LqZkeQhY"  # Insira seu token aqui

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(handle_promo_choice))

    print("🤖 Bot iniciado com sucesso!")
    await app.initialize()
    await app.start()

    try:
        await app.updater.start_polling()
        await asyncio.Future()  # Mantém o bot ativo
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("🤖 Bot encerrado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🤖 Bot encerrado.")
