import telebot
import os
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# user ma'lumotlari
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "riding": False
        }
    return users[user_id]

# MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔋 Balance", "💳 Top Up")
    markup.add("🛴 Start Ride", "❌ End Ride")
    return markup

# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Botga xush kelibsiz 🚀",
        reply_markup=main_menu()
    )

# BALANCE
@bot.message_handler(func=lambda m: m.text == "🔋 Balance")
def balance(message):
    user = get_user(message.chat.id)
    bot.send_message(message.chat.id, f"Balansingiz: {user['balance']} so'm")

# TOP UP
@bot.message_handler(func=lambda m: m.text == "💳 Top Up")
def topup(message):
    user = get_user(message.chat.id)
    user['balance'] += 5000
    bot.send_message(message.chat.id, "5000 so'm qo'shildi 💰")

# START RIDE
@bot.message_handler(func=lambda m: m.text == "🛴 Start Ride")
def start_ride(message):
    user = get_user(message.chat.id)

    if user["balance"] < 1000:
        bot.send_message(message.chat.id, "Balans yetarli emas ❌")
        return

    user["riding"] = True
    bot.send_message(message.chat.id, "Skuter ochildi 🛴")

# END RIDE
@bot.message_handler(func=lambda m: m.text == "❌ End Ride")
def end_ride(message):
    user = get_user(message.chat.id)

    if not user["riding"]:
        bot.send_message(message.chat.id, "Siz minmayapsiz ❌")
        return

    user["riding"] = False
    user["balance"] -= 1000

    bot.send_message(message.chat.id, "Ride tugadi ✅ 1000 so'm yechildi")

bot.infinity_polling()
