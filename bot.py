import telebot
from telebot import types
import time
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 8133027931

# SKUTERLAR (lokatsiya bilan)
scooters = {
    "SC001": {"busy": False, "lat": 39.7747, "lon": 64.4286},
    "SC002": {"busy": False, "lat": 39.7750, "lon": 64.4290}
}

users = {}

# MENU
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Balans", "➕ Pul qo‘shish")
    markup.row("🛴 Skuter olish", "❌ Haydashni tugatish")
    markup.row("📍 Skuterlar xaritada")
    return markup

# START + QR
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    args = message.text.split()

    if uid not in users:
        users[uid] = {
            "balance": 10000,
            "riding": False,
            "scooter": None
        }

    # QR orqali kirsa
    if len(args) > 1:
        scooter_id = args[1].upper()

        if scooter_id in scooters and not scooters[scooter_id]["busy"]:
            users[uid]["riding"] = True
            users[uid]["scooter"] = scooter_id
            scooters[scooter_id]["busy"] = True

            bot.send_message(uid, f"🚀 {scooter_id} skuter boshlandi!")

            start_timer(uid, scooter_id)

        else:
            bot.send_message(uid, "❗ Skuter band yoki yo‘q")

    else:
        bot.send_message(uid, "Bot ishga tushdi ✅", reply_markup=menu())

# TIMER (300 so'm/minut)
def start_timer(uid, sid):
    def ride():
        while users[uid]["riding"]:
            time.sleep(60)

            if not users[uid]["riding"]:
                break

            if users[uid]["balance"] >= 300:
                users[uid]["balance"] -= 300
                bot.send_message(uid, f"💸 1 minut o'tdi\nBalans: {users[uid]['balance']} so'm")
            else:
                bot.send_message(uid, "❗ Balans tugadi")
                users[uid]["riding"] = False
                scooters[sid]["busy"] = False
                break

    threading.Thread(target=ride, daemon=True).start()

# SKUTER OLISH (qo‘lda ID)
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def get_scooter(message):
    bot.send_message(message.chat.id, "Skuter ID kiriting (masalan: SC001)")

@bot.message_handler(func=lambda m: m.text.startswith("SC"))
def start_ride(message):
    uid = message.chat.id
    sid = message.text.upper()

    if sid not in scooters:
        bot.send_message(uid, "❗ Bunday skuter yo‘q")
        return

    if scooters[sid]["busy"]:
        bot.send_message(uid, "❗ Skuter band")
        return

    if users[uid]["riding"]:
        bot.send_message(uid, "❗ Siz allaqachon haydalyapsiz")
        return

    scooters[sid]["busy"] = True
    users[uid]["riding"] = True
    users[uid]["scooter"] = sid

    bot.send_message(uid, f"🚀 {sid} boshlandi!")
    start_timer(uid, sid)

# STOP
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def stop(message):
    uid = message.chat.id
    user = users[uid]

    if not user["riding"]:
        bot.send_message(uid, "❗ Siz haydamayapsiz")
        return

    sid = user["scooter"]

    user["riding"] = False
    scooters[sid]["busy"] = False

    bot.send_message(uid, "📸 Rasm yuboring")

# RASM
@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.send_message(message.chat.id, "📍 Lokatsiya yuboring")

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
                   caption=f"User: {message.chat.id}")

# LOKATSIYA
@bot.message_handler(content_types=['location'])
def location(message):
    bot.send_message(message.chat.id, "✅ Ride tugadi, rahmat!")

    bot.send_location(ADMIN_ID,
                      message.location.latitude,
                      message.location.longitude)

# XARITA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar xaritada")
def show_map(message):
    for sid, data in scooters.items():
        bot.send_location(message.chat.id, data["lat"], data["lon"])
        bot.send_message(message.chat.id, f"{sid} skuter")

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balance(message):
    bot.send_message(message.chat.id,
                     f"💰 Balans: {users[message.chat.id]['balance']} so'm")

# TOP UP
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def topup(message):
    bot.send_message(message.chat.id, "Admin bilan bog‘laning")

bot.infinity_polling()
