import telebot
import time
import threading

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
ADMIN_CODE = "1234"
PRICE_PER_MINUTE = 500

bot = telebot.TeleBot(TOKEN)

user_step = {}
user_balance = {}
user_time = {}
active_users = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    if chat_id not in user_balance:
        user_balance[chat_id] = 5000  # boshlang'ich balans

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛴 Skuterni ochish", "🔒 Skuterni yopish", "💰 Balans")

    bot.send_message(chat_id, "Kerakli bo'limni tanlang:", reply_markup=markup)

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    bot.send_message(message.chat.id, f"Sizning balans: {user_balance[message.chat.id]} so'm")

# SKUTER OCHISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuterni ochish")
def open_scooter(message):
    user_step[message.chat.id] = "kod"
    bot.send_message(message.chat.id, "Kod kiriting:")

# KOD TEKSHIRISH
@bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "kod")
def check_code(message):
    chat_id = message.chat.id

    if message.text == ADMIN_CODE:
        if user_balance.get(chat_id, 0) < PRICE_PER_MINUTE:
            bot.send_message(chat_id, "❌ Balans yetarli emas!")
            return

        bot.send_message(chat_id, "✅ Skuter ochildi!")
        user_step[chat_id] = None
        active_users[chat_id] = True

        # vaqtni boshlash
        threading.Thread(target=start_timer, args=(chat_id,)).start()
    else:
        bot.send_message(chat_id, "❌ Noto‘g‘ri kod!")

# TIMER
def start_timer(chat_id):
    while active_users.get(chat_id):
        time.sleep(60)

        if user_balance[chat_id] >= PRICE_PER_MINUTE:
            user_balance[chat_id] -= PRICE_PER_MINUTE
            bot.send_message(chat_id, f"⏱ 1 minut o'tdi. -500 so'm\nQoldiq: {user_balance[chat_id]}")
        else:
            bot.send_message(chat_id, "❌ Pul tugadi! Skuter yopildi.")
            active_users[chat_id] = False
            break

# SKUTER YOPISH
@bot.message_handler(func=lambda m: m.text == "🔒 Skuterni yopish")
def close_scooter(message):
    chat_id = message.chat.id
    active_users[chat_id] = False
    user_step[chat_id] = "rasm"
    bot.send_message(chat_id, "Rasm yuboring:")

# RASM
@bot.message_handler(content_types=['photo'])
def photo(message):
    chat_id = message.chat.id
    if user_step.get(chat_id) == "rasm":
        bot.send_message(chat_id, "📸 Rasm qabul qilindi. Skuter yopildi ✅")
        user_step[chat_id] = None

# DEFAULT
@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, "Menyudan foydalaning ⬇️")

bot.polling()
