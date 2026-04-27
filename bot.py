import telebot
import os
import time
import threading
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

PRICE_PER_MINUTE = 300
PRICE_PER_SECOND = PRICE_PER_MINUTE / 60

users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "riding": False
        }
    return users[user_id]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔋 Balance", "💳 Top Up")
    markup.add("🛴 Start Ride", "❌ End Ride")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Botga xush kelibsiz 🚀", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔋 Balance")
def balance(message):
    user = get_user(message.chat.id)
    bot.send_message(message.chat.id, f"Balans: {int(user['balance'])} so'm")

@bot.message_handler(func=lambda m: m.text == "💳 Top Up")
def topup(message):
    user = get_user(message.chat.id)
    user["balance"] += 5000
    bot.send_message(message.chat.id, "5000 so'm qo'shildi 💰")

def ride_process(user_id):
    while users[user_id]["riding"]:
        time.sleep(10)

        users[user_id]["balance"] -= PRICE_PER_SECOND * 10

        bot.send_message(
            user_id,
            f"💸 Balans kamaymoqda: {int(users[user_id]['balance'])} so'm"
        )

        if users[user_id]["balance"] <= 0:
            users[user_id]["riding"] = False
            bot.send_message(user_id, "Balans tugadi ❌ Ride to‘xtadi")
            break

@bot.message_handler(func=lambda m: m.text == "🛴 Start Ride")
def start_ride(message):
    user = get_user(message.chat.id)

    if user["balance"] < 300:
        bot.send_message(message.chat.id, "Balans yetarli emas ❌")
        return

    user["riding"] = True
    bot.send_message(message.chat.id, "Ride boshlandi 🛴")

    threading.Thread(target=ride_process, args=(message.chat.id,)).start()

@bot.message_handler(func=lambda m: m.text == "❌ End Ride")
def end_ride(message):
    user = get_user(message.chat.id)

    if not user["riding"]:
        bot.send_message(message.chat.id, "Siz ride boshlamagansiz ❌")
        return

    user["riding"] = False
    bot.send_message(message.chat.id, "Ride tugadi ✅")

bot.infinity_polling()
