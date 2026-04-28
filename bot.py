import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import threading

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
bot = telebot.TeleBot(TOKEN)

user_balance = {}
user_state = {}
ride_data = {}

SKUTER_PRICE = 5000
PRICE_PER_MIN = 500
KARTA = "4023060516859138"

# 🔘 MENU
def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛴 Skuter olish"))
    kb.add(KeyboardButton("🛑 Skuter yopish"))
    kb.add(KeyboardButton("➕ Pul qo‘shish"))
    kb.add(KeyboardButton("💰 Balans"))
    return kb

# 🚀 START
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    if user_id not in user_balance:
        user_balance[user_id] = 0

    bot.send_message(msg.chat.id, "🚀 Xush kelibsiz!", reply_markup=menu())

# 💰 BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(msg):
    user_id = msg.from_user.id
    bal = user_balance.get(user_id, 0)
    bot.send_message(msg.chat.id, f"💰 Sizning balans: {bal} so‘m")

# ➕ PUL QO‘SHISH (test)
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def add_money(msg):
    user_id = msg.from_user.id
    user_balance[user_id] = user_balance.get(user_id, 0) + 5000

    bot.send_message(msg.chat.id,
        f"""✅ 5000 so‘m qo‘shildi
💰 Balans: {user_balance[user_id]}

💳 Real to‘lov uchun:
{KARTA}""")

# 🛴 SKUTER OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def skuter_olish(msg):
    user_id = msg.from_user.id

    if user_balance.get(user_id, 0) < SKUTER_PRICE:
        bot.send_message(msg.chat.id,
        f"""❌ Balans yetarli emas!

💳 Karta:
{KARTA}""")
    else:
        user_state[user_id] = "kod"
        bot.send_message(msg.chat.id, "🔑 Skuter kodini kiriting:")

# 🔄 REAL TIME RIDE
def ride_worker(user_id, chat_id):
    while True:
        time.sleep(60)

        if user_id not in ride_data or not ride_data[user_id]["active"]:
            break

        user_balance[user_id] -= PRICE_PER_MIN

        if user_balance[user_id] <= 0:
            ride_data[user_id]["active"] = False

            bot.send_message(chat_id,
            "❌ Balans tugadi!\n🛑 Skuter avtomatik yopildi")

            break

# 🔑 KOD KIRITISH
@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    text = msg.text

    if user_state.get(user_id) == "kod":
        if text == "1234":
            user_balance[user_id] -= SKUTER_PRICE

            ride_data[user_id] = {"active": True}

            threading.Thread(target=ride_worker, args=(user_id, chat_id)).start()

            user_state[user_id] = None

            bot.send_message(chat_id,
            f"""✅ Skuter ochildi! 🛴

💰 Balans: {user_balance[user_id]}
⛔ Tugatish: "Skuter yopish" """)
        else:
            bot.send_message(chat_id, "❌ Kod noto‘g‘ri!")

# 🛑 SKUTER YOPISH
@bot.message_handler(func=lambda m: m.text == "🛑 Skuter yopish")
def stop(msg):
    user_id = msg.from_user.id

    if user_id not in ride_data or not ride_data[user_id]["active"]:
        bot.send_message(msg.chat.id, "❗ Siz minmayapsiz")
        return

    ride_data[user_id]["active"] = False

    bot.send_message(msg.chat.id,
    f"""🛑 Skuter yopildi!

💰 Qoldiq: {user_balance[user_id]} so‘m""")

# ▶️ BOTNI ISHGA TUSHIRISH
bot.infinity_polling()
