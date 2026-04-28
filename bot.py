import telebot

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
ADMIN_ID = 8133027931  # o'zingni telegram id
CARD = "4023060516859138"
PRICE_PER_MINUTE = 500

bot = telebot.TeleBot(TOKEN)

user_step = {}
user_balance = {}
user_scooter_code = {}

def check_user(chat_id):
    if chat_id not in user_balance:
        user_balance[chat_id] = 0

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛴 Skuterni ochish", "💰 Balans")
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    check_user(message.chat.id)
    bot.send_message(message.chat.id, f"Balans: {user_balance[message.chat.id]} so'm")

# SKUTER OCHISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuterni ochish")
def open_scooter(message):
    bot.send_message(message.chat.id, "Skuter kodini kiriting:")
    user_step[message.chat.id] = "kod"

# KOD
@bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "kod")
def get_code(message):
    chat_id = message.chat.id
    check_user(chat_id)

    user_scooter_code[chat_id] = message.text

    if user_balance[chat_id] < PRICE_PER_MINUTE:
        bot.send_message(chat_id,
            f"❌ Balans yetarli emas!\n\n"
            f"💳 Pul tashlang:\n{CARD}\n\n"
            f"Chek yuboring:")
        user_step[chat_id] = "chek"
    else:
        bot.send_message(chat_id, "✅ Skuter ochildi!")
        user_step[chat_id] = None

# CHEK QABUL
@bot.message_handler(content_types=['photo'])
def get_check(message):
    chat_id = message.chat.id

    if user_step.get(chat_id) == "chek":
        bot.send_message(chat_id, "⏳ Tekshirilmoqda...")

        # adminga yuborish
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
            caption=f"Yangi to'lov!\nUser: {chat_id}\nKod: {user_scooter_code.get(chat_id)}")

# ADMIN TASDIQLASH
@bot.message_handler(commands=['ok'])
def admin_ok(message):
    if message.chat.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])
            user_balance[user_id] += 5000  # qancha tushsa o'zgartir

            bot.send_message(user_id, "✅ To'lov tasdiqlandi!\nSkuter ochildi 🚀")
        except:
            bot.send_message(message.chat.id, "Xato format")

bot.polling()
