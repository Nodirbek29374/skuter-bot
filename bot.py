   import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

users = {}

menu = ReplyKeyboardMarkup([
    ["💰 Balans", "➕ Pul qo‘shish"],
    ["🛴 Haydashni boshlash", "❌ Haydashni tugatish"],
    ["📍 Skuterlar xaritada"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users[user_id] = {"balance": 10000, "ride": False}
    await update.message.reply_text("Assalomu alaykum!", reply_markup=menu)

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in users:
        users[user_id] = {"balance": 10000, "ride": False}

    user = users[user_id]

    if text == "💰 Balans":
        await update.message.reply_text(f"Balans: {user['balance']} so‘m")

    elif text == "➕ Pul qo‘shish":
        await update.message.reply_text("Admin bilan bog‘laning")

    elif text == "🛴 Haydashni boshlash":
        user["ride"] = True
        await update.message.reply_text("Haydash boshlandi")

    elif text == "❌ Haydashni tugatish":
        user["ride"] = False
        await update.message.reply_text("Rasm yuboring")

    elif text == "📍 Skuterlar xaritada":
        await update.message.reply_text("Xarita hali tayyor emas")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    await update.message.reply_text("Endi lokatsiya yuboring")

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"User: {user_id}"
    )

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    loc = update.message.location

    await context.bot.send_location(
        chat_id=ADMIN_ID,
        latitude=loc.latitude,
        longitude=loc.longitude
    )

    await update.message.reply_text("✅ Tugadi")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, message))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.LOCATION, location))

    app.run_polling()

if __name__ == "__main__":
    main()
