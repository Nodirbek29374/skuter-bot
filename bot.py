import telebot
from telebot import types
import time
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 8133027931  # o'zingni ID

users = {}

# MENU
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Balans", "➕ Pul qo‘shish")
    markup.row("🛴 Haydashni boshlash", "❌ Haydashni tugatish")
    return markup

# START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if user_id not in users:
        users[user_id] = {
            "balance": 10000,
            "riding": False,
            "last_time": 0
        }

    bot.send_message(user_id, "Bot ishga tushdi ✅", reply_markup=menu())

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balance(message):
    user = users[message.chat.id]
    bot.send_message(message.chat.id, f"💰 Balans: {user['balance']} so'm")

# TOP UP
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def topup(message):
    bot.send_message(message.chat.id, "Admin bilan bog‘laning")

# START RIDE
@bot.message_handler(func=lambda m: m.text == "🛴 Haydashni boshlash")
def start_ride(message):
    user = users[message.chat.id]

    if user["riding"]:
        bot.send_message(message.chat.id, "Allaqachon haydalyapti!")
        return

    user["riding"] = True
    user["last_time"] = time.time()

    bot.send_message(message.chat.id, "🚀 Haydash boshlandi!")

    # minutiga pul yechish
    def ride():
        while user["riding"]:
            time.sleep(60)

            if user["balance"] >= 300:
                user["balance"] -= 300
                bot.send_message(message.chat.id, f"💸 1 minut o'tdi\nBalans: {user['balance']} so'm")
            else:
                bot.send_message(message.chat.id, "❗ Balans tugadi")
                user["riding"] = False
                break

    threading.Thread(target=ride).start()

# END RIDE
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def end_ride(message):
    user = users[message.chat.id]

    if not user["riding"]:
        bot.send_message(message.chat.id, "Siz haydamayapsiz")
        return

    user["riding"] = False

    bot.send_message(message.chat.id, "📸 Skuter rasmini yuboring")

# RASM QABUL QILISH
@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.send_message(message.chat.id, "📍 Endi lokatsiya yuboring")

    # adminga yuborish
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"User: {message.chat.id}")

# LOKATSIYA
@bot.message_handler(content_types=['location'])
def location(message):
    bot.send_message(message.chat.id, "✅ Ride tugadi, rahmat!")

    # adminga yuborish
    bot.send_location(ADMIN_ID, message.location.latitude, message.location.longitude)

# DEFAULT
@bot.message_handler(func=lambda m: True)
def other(message):
    bot.send_message(message.chat.id, "Tugmalardan foydalaning", reply_markup=menu())

bot.infinity_polling()    
