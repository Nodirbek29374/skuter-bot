import telebot

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8133027931  # 👉 o'zingni ID qo'y
user_balance = {}
user_states = {}
user_code = "1234"

# MENYULAR
def user_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balans", "➕ Pul qo'shish")
    markup.add("🛴 Skuter olish", "❌ Haydashni tugatish")
    return markup

def admin_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Balans", "➕ Pul qo'shish")
    markup.add("🛴 Skuter olish", "❌ Haydashni tugatish")
    markup.add("👑 Admin panel")
    return markup

# START
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_balance[chat_id] = 20000

    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "👑 Admin sifatida kirdingiz", reply_markup=admin_menu())
    else:
        bot.send_message(chat_id, "Tanlang:", reply_markup=user_menu())

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    bot.send_message(message.chat.id, f"💰 Balans: {user_balance.get(message.chat.id,0)} so'm")

# PUL QO‘SHISH (USER TEST)
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo'shish")
def add_money(message):
    user_balance[message.chat.id] += 10000
    bot.send_message(message.chat.id, "✅ 10000 so'm qo'shildi")

# SKUTER OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def skuter_olish(message):
    bot.send_message(message.chat.id, "🔑 Skuter kodini kiriting:")
    user_states[message.chat.id] = "waiting_code"

# KOD TEKSHIRISH
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_code(message):
    chat_id = message.chat.id

    if user_states.get(chat_id) == "waiting_code":
        if message.text == user_code:
            bot.send_message(chat_id, "✅ Skuter ochildi!")
            user_states[chat_id] = None
        else:
            bot.send_message(chat_id, "❌ Noto‘g‘ri kod!")

# HAYDASHNI TUGATISH
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def stop_ride(message):
    bot.send_message(message.chat.id, "📸 Skuter rasmini yuboring:")
    user_states[message.chat.id] = "waiting_photo"

# RASM QABUL QILISH
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if user_states.get(message.chat.id) == "waiting_photo":
        bot.send_message(message.chat.id, "✅ Skuter yopildi. Rahmat!")
        user_states[message.chat.id] = None

# ================= ADMIN PANEL =================

# ADMIN PANELGA KIRISH
@bot.message_handler(func=lambda m: m.text == "👑 Admin panel")
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💸 Pul berish", "📊 Statistika")
    markup.add("🔙 Orqaga")

    bot.send_message(message.chat.id, "👑 Admin panel:", reply_markup=markup)

# ORQAGA
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔙 Asosiy menyu", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "🔙 Asosiy menyu", reply_markup=user_menu())

# PUL BERISH BOSHLASH
@bot.message_handler(func=lambda m: m.text == "💸 Pul berish")
def give_money(message):
    if message.chat.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id, "User ID va summa yuboring:\nMasalan: 123456789 10000")
    user_states[message.chat.id] = "admin_give_money"

# PUL BERISH AMALGA OSHIRISH
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "admin_give_money")
def process_give_money(message):
    try:
        user_id, amount = map(int, message.text.split())
        user_balance[user_id] = user_balance.get(user_id, 0) + amount

        bot.send_message(message.chat.id, "✅ Pul berildi")
        bot.send_message(user_id, f"💰 Sizga {amount} so'm berildi")

    except:
        bot.send_message(message.chat.id, "❌ Xato format!")

    user_states[message.chat.id] = None

# STATISTIKA
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats(message):
    if message.chat.id != ADMIN_ID:
        return

    total_users = len(user_balance)
    bot.send_message(message.chat.id, f"👥 Foydalanuvchilar soni: {total_users}")

# =================================================

bot.infinity_polling()
