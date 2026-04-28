import telebot
from telebot import types
import time

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
ADMIN_ID = 8133027931  # ⬅️ o‘zingni telegram ID qo‘y

bot = telebot.TeleBot(TOKEN)

# ===== DATA =====
users = {}
user_step = {}

SKUTERS = {
    "1234": {"status": "free"},
    "5678": {"status": "free"},
}

PRICE_PER_MIN = 1000
FINE = 5000  # rasm yubormasa jarima

# ===== MENU =====
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balans", "+ Pul qo‘shish")
    markup.add("🛴 Skuter olish", "❌ Haydashni tugatish")
    return markup

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id

    if uid not in users:
        users[uid] = {
            "balance": 10000,
            "ride": None,
            "skuter": None,
            "waiting_photo_time": None
        }

    bot.send_message(message.chat.id, "Tanlang:", reply_markup=menu())

# ===== BALANS =====
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, f"💰 Balans: {users[uid]['balance']} so‘m")

# ===== PUL QO‘SHISH =====
@bot.message_handler(func=lambda m: m.text == "+ Pul qo‘shish")
def pul(message):
    uid = message.from_user.id
    users[uid]["balance"] += 5000
    bot.send_message(message.chat.id, "✅ 5000 so‘m qo‘shildi")

# ===== SKUTER OLISH =====
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def ask_code(message):
    uid = message.from_user.id

    if users[uid]["ride"] is not None:
        bot.send_message(message.chat.id, "❗ Siz allaqachon haydayapsiz")
        return

    user_step[uid] = "code"
    bot.send_message(message.chat.id, "🔑 Skuter kodini kiriting:")

# ===== STOP =====
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def stop(message):
    uid = message.from_user.id

    if users[uid]["ride"] is None:
        bot.send_message(message.chat.id, "❗ Siz haydamayapsiz")
        return

    user_step[uid] = "photo"
    users[uid]["waiting_photo_time"] = time.time()

    bot.send_message(message.chat.id, "📸 Skuter rasmini yuboring (60 sekund ichida):")

# ===== RASM =====
@bot.message_handler(content_types=['photo'])
def photo(message):
    uid = message.from_user.id

    if user_step.get(uid) == "photo":
        start_time = users[uid]["ride"]
        minutes = int((time.time() - start_time) / 60) + 1
        cost = minutes * PRICE_PER_MIN

        users[uid]["balance"] -= cost
        users[uid]["ride"] = None

        code = users[uid]["skuter"]
        if code:
            SKUTERS[code]["status"] = "free"

        user_step[uid] = None

        # ADMIN ga yuborish
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=f"📸 Skuter rasmi\nUser: {uid}\nSkuter: {code}"
        )

        bot.send_message(
            message.chat.id,
            f"🛑 Tugadi\n⏱ {minutes} min\n💸 {cost} so‘m yechildi\n📸 Rasm qabul qilindi"
        )

# ===== TEXT =====
@bot.message_handler(func=lambda m: True)
def all_msg(message):
    uid = message.from_user.id

    # kod kiritish
    if user_step.get(uid) == "code":
        code = message.text

        if code in SKUTERS and SKUTERS[code]["status"] == "free":
            if users[uid]["balance"] < PRICE_PER_MIN:
                bot.send_message(message.chat.id, "❌ Balans yetarli emas")
                return

            SKUTERS[code]["status"] = "busy"
            users[uid]["ride"] = time.time()
            users[uid]["skuter"] = code
            user_step[uid] = None

            bot.send_message(message.chat.id, "🛴 Skuter ochildi 🚀")
        else:
            bot.send_message(message.chat.id, "❌ Kod noto‘g‘ri yoki band")

    else:
        bot.send_message(message.chat.id, "❗ Tugmalardan foydalaning")

# ===== JARIMA CHECK =====
def check_fines():
    while True:
        now = time.time()
        for uid in users:
            if user_step.get(uid) == "photo":
                wait = users[uid]["waiting_photo_time"]
                if wait and now - wait > 60:
                    users[uid]["balance"] -= FINE
                    user_step[uid] = None
                    users[uid]["ride"] = None

                    bot.send_message(uid, f"⏰ Vaqt tugadi!\n💸 {FINE} so‘m jarima")

        time.sleep(10)

import threading
threading.Thread(target=check_fines).start()

# ===== RUN =====
bot.polling(none_stop=True)
