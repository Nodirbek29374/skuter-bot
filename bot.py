 import telebot
import time
import threading

TOKEN = "SENING_TOKENINGNI_BU_YERGA_QO'Y"

bot = telebot.TeleBot(TOKEN)

users = {}

PRICE_PER_MINUTE = 300


# START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    users[user_id] = {
        "balance": 0,
        "riding": False
    }

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balans", "➕ Pul qo‘shish")
    markup.add("🛴 Haydashni boshlash", "❌ Haydashni tugatish")
    markup.add("📍 Skuterlar xaritada")

    bot.send_message(user_id, "Assalomu alaykum!", reply_markup=markup)


# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balance(message):
    user = users.get(message.chat.id)
    if user:
        bot.send_message(message.chat.id, f"Balans: {user['balance']} so‘m")


# PUL QO‘SHISH
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def add_money(message):
    users[message.chat.id]["balance"] += 10000
    bot.send_message(message.chat.id, "10000 so‘m qo‘shildi")


# HAYDASHNI BOSHLASH
@bot.message_handler(func=lambda m: m.text == "🛴 Haydashni boshlash")
def start_ride(message):
    user = users[message.chat.id]

    if user["balance"] < 300:
        bot.send_message(message.chat.id, "Balans yetarli emas!")
        return

    user["riding"] = True
    bot.send_message(message.chat.id, "🚀 Haydash boshlandi")

    threading.Thread(target=ride_timer, args=(message.chat.id,)).start()


def ride_timer(user_id):
    while users[user_id]["riding"]:
        time.sleep(60)

        if users[user_id]["balance"] < PRICE_PER_MINUTE:
            bot.send_message(user_id, "❌ Pul tugadi!")
            users[user_id]["riding"] = False
            return

        users[user_id]["balance"] -= PRICE_PER_MINUTE

        bot.send_message(
            user_id,
            f"💸 1 minut o‘tdi\nBalans: {users[user_id]['balance']} so‘m"
        )


# HAYDASHNI TUGATISH
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def end_ride(message):
    users[message.chat.id]["riding"] = False

    bot.send_message(message.chat.id, "📸 Skuter rasmini yuboring")


# RASM
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.send_message(message.chat.id, "📍 Endi lokatsiya yuboring")


# LOKATSIYA
@bot.message_handler(content_types=['location'])
def get_location(message):
    bot.send_message(message.chat.id, "✅ Ride tugadi, rahmat!")


# XARITA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar xaritada")
def map(message):
    bot.send_location(message.chat.id, 41.3111, 69.2797)


print("Bot ishlayapti...")
bot.infinity_polling()
