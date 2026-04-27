            import telebot
from telebot import types
import time

BOT_TOKEN = "TOKENINGNI_QO'Y"

bot = telebot.TeleBot(BOT_TOKEN)

users = {}

# 🔘 MENU
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Balans", "➕ Pul qo‘shish")
    markup.row("🛴 Skuter olish", "❌ Haydashni tugatish")
    markup.row("📍 Skuterlar xaritada")
    return markup

# 🚀 START
@bot.message_handler(commands=['start'])
def start(msg):
    users[msg.chat.id] = {
        "balans": 10000,
        "ride": False,
        "start_time": 0
    }

    bot.send_message(
        msg.chat.id,
        "Xush kelibsiz!",
        reply_markup=main_menu()
    )

# 💰 BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(msg):
    bal = users[msg.chat.id]["balans"]
    bot.send_message(msg.chat.id, f"💰 Balans: {bal} so‘m", reply_markup=main_menu())

# ➕ PUL QO‘SHISH
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def topup(msg):
    users[msg.chat.id]["balans"] += 5000
    bot.send_message(msg.chat.id, "✅ 5000 so‘m qo‘shildi", reply_markup=main_menu())

# 🛴 START RIDE
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def start_ride(msg):
    user = users[msg.chat.id]

    if user["ride"]:
        bot.send_message(msg.chat.id, "❗ Siz allaqachon haydamoqdasiz", reply_markup=main_menu())
        return

    if user["balans"] < 300:
        bot.send_message(msg.chat.id, "❌ Balans yetarli emas", reply_markup=main_menu())
        return

    user["ride"] = True
    user["start_time"] = time.time()

    bot.send_message(msg.chat.id, "🟢 Haydash boshlandi", reply_markup=main_menu())

# ❌ END RIDE
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def end_ride(msg):
    user = users[msg.chat.id]

    if not user["ride"]:
        bot.send_message(msg.chat.id, "❗ Siz haydamayapsiz", reply_markup=main_menu())
        return

    minutes = int((time.time() - user["start_time"]) / 60)
    cost = minutes * 300

    user["balans"] -= cost
    user["ride"] = False

    bot.send_message(
        msg.chat.id,
        f"🛑 Haydash tugadi\n⏱ {minutes} minut\n💸 {cost} so‘m yechildi",
        reply_markup=main_menu()
    )

# 📍 XARITA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar xaritada")
def map_func(msg):
    bot.send_message(
        msg.chat.id,
        "📍 Skuter shu yerda:\nhttps://maps.google.com/?q=41.3111,69.2797",
        reply_markup=main_menu()
    )

bot.infinity_polling()
