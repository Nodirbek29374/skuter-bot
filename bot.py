import telebot
import os
import time
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

PRICE_PER_MINUTE = 300  # 1 minut = 300 so'm

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "riding": False,
            "start_time": 0
        }
    return users[user_id]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔋 Balance", "💳 Top Up")
    markup.add("🛴 Start Ride", "❌ End Ride")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Botga xush kelibsiz 🚀",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🔋 Balance")
def balance(message):
    user = get_user(message.chat.id)
    bot.send_message(message.chat.id, f"Balans: {user['balance']} so'm")

@bot.message_handler(func=lambda m: m.text == "💳 Top Up")
def topup(message):
    user = get_user(message.chat.id)
    user["balance"] += 5000
    bot.send_message(message.chat.id, "5000 so'm qo'shildi 💰")

@bot.message_handler(func=lambda m: m.text == "🛴 Start Ride")
def start_ride(message):
    user = get_user(message.chat.id)

    if user["balance"] < 300:
        bot.send_message(message.chat.id, "Balans yetarli emas ❌")
        return

    user["riding"] = True
    user["start_time"] = time.time()

    bot.send_message(message.chat.id, "Skuter boshlandi 🛴")

@bot.message_handler(func=lambda m: m.text == "❌ End Ride")
def end_ride(message):
    user = get_user(message.chat.id)

    if not user["riding"]:
        bot.send_message(message.chat.id, "Siz ride boshlamagansiz ❌")
        return

    end_time = time.time()
    duration = int((end_time - user["start_time"]) / 60)

    if duration == 0:
        duration = 1  # minimum 1 minut

    cost = duration * PRICE_PER_MINUTE

    user["balance"] -= cost
    user["riding"] = False

    bot.send_message(
        message.chat.id,
        f"Ride tugadi ✅\nVaqt: {duration} minut\nNarx: {cost} so'm"
    )

bot.infinity_polling()
