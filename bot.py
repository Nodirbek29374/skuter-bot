   import telebot
import time
import threading

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
bot = telebot.TeleBot(TOKEN)

users = {}

# MENU
def menu():
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💰 Balans", "➕ Pul qo'shish")
    kb.add("🛴 Haydashni boshlash", "❌ Haydashni tugatish")
    kb.add("📍 Skuterlar xaritada")
    return kb

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    users[uid] = {"balans": 10000, "ride": False}
    bot.send_message(uid, "Xush kelibsiz!", reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def handler(msg):
    uid = msg.from_user.id

    if uid not in users:
        users[uid] = {"balans": 0, "ride": False}

    if msg.text == "💰 Balans":
        bot.send_message(uid, f"Balans: {users[uid]['balans']} so'm")

    elif msg.text == "➕ Pul qo'shish":
        users[uid]['balans'] += 5000
        bot.send_message(uid, "5000 so'm qo'shildi")

    elif msg.text == "🛴 Haydashni boshlash":
        if users[uid]['balans'] < 300:
            bot.send_message(uid, "Balans yetarli emas")
            return

        users[uid]['ride'] = True
        bot.send_message(uid, "Haydash boshlandi")

        def ride():
            while users[uid]['ride']:
                time.sleep(60)
                users[uid]['balans'] -= 300
                bot.send_message(uid, f"1 minut o'tdi\nBalans: {users[uid]['balans']} so'm")

                if users[uid]['balans'] <= 0:
                    users[uid]['ride'] = False
                    bot.send_message(uid, "Balans tugadi!")
                    break

        threading.Thread(target=ride).start()

    elif msg.text == "❌ Haydashni tugatish":
        users[uid]['ride'] = False
        bot.send_message(uid, "Ride tugadi")

    elif msg.text == "📍 Skuterlar xaritada":
        bot.send_location(uid, 39.6542, 66.9597)  # Buxoro misol

bot.infinity_polling()  
