 import telebot
from telebot import types
import time

BOT_TOKEN = "TOKENINGNI_QO'Y"

bot = telebot.TeleBot(BOT_TOKEN)

users = {}

def get_user(chat_id):
    if chat_id not in users:
        users[chat_id] = {
            "balans": 10000,
            "ride": False,
            "start_time": 0
        }
    return users[chat_id]

# MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Balans", "➕ Pul qo‘shish")
    markup.row("🛴 Skuter olish", "❌ Haydashni tugatish")
    markup.row("📍 Skuterlar xaritada")
    return markup

# START
@bot.message_handler(commands=['start'])
def start(msg):
    get_user(msg.chat.id)
    bot.send_message(msg.chat.id, "Xush kelibsiz!", reply_markup=main_menu())

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(msg):
    user = get_user(msg.chat.id)
    bot.send_message(msg.chat.id, f"💰 Balans: {user['balans']} so‘m", reply_markup=main_menu())

# TOP UP
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def topup(msg):
    user = get_user(msg.chat.id)
    user["balans"] += 5000
    bot.send_message(msg.chat.id, "✅ 5000 so‘m qo‘shildi", reply_markup=main_menu())

# START RIDE
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def start_ride(msg):
    user = get_user(msg.chat.id)

    if user["ride"]:
        bot.send_message(msg.chat.id, "❗ Siz allaqachon haydamoqdasiz", reply_markup=main_menu())
        return

    if user["balans"] < 300:
        bot.send_message(msg.chat.id, "❌ Balans yetarli emas", reply_markup=main_menu())
        return

    user["ride"] = True
    user["start_time"] = time.time()

    bot.send_message(msg.chat.id, "🟢 Haydash boshlandi", reply_markup=main_menu())

# END RIDE
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def end_ride(msg):
    user = get_user(msg.chat.id)

    if not user["ride"]:
        bot.send_message(msg.chat.id, "❗ Siz haydamayapsiz", reply_markup=main_menu())
        return

    minutes = int((time.time() - user["start_time"]) / 60)
    if minutes == 0:
        minutes = 1

    cost = minutes * 300

    user["balans"] -= cost
    user["ride"] = False

    bot.send_message(
        msg.chat.id,
        f"🛑 Haydash tugadi\n⏱ {minutes} minut\n💸 {cost} so‘m yechildi",
        reply_markup=main_menu()
    )

# MAP
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar xaritada")
def map_func(msg):
    bot.send_location(msg.chat.id, 41.3111, 69.2797)
    bot.send_message(msg.chat.id, "📍 Skuter joylashuvi", reply_markup=main_menu())

# ERROR HANDLER (MUHIM)
@bot.message_handler(func=lambda m: True)
def fallback(msg):
    bot.send_message(msg.chat.id, "❗ Noto‘g‘ri buyruq", reply_markup=main_menu())

bot.infinity_polling()           
