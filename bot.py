import telebot

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
ADMIN_ID =8133027931
CARD = "8600 1234 5678 9012"

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
    bot.send_message(message.chat.id, f"💰 Balans: {user_balance[message.chat.id]} so'm")

# SKUTER OCHISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuterni ochish")
def open_scooter(message):
    bot.send_message(message.chat.id, "🔢 Skuter kodini kiriting:")
    user_step[message.chat.id] = "kod"

# KOD
@bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "kod")
def get_code(message):
    chat_id = message.chat.id
    check_user(chat_id)

    user_scooter_code[chat_id] = message.text

    if user_balance[chat_id] < 500:
        bot.send_message(chat_id,
            f"❌ Balans yetarli emas!\n\n💳 {CARD}\n\n📸 Chek yuboring:")
        user_step[chat_id] = "chek"
    else:
        bot.send_message(chat_id, "✅ Skuter ochildi!")

# CHEK
@bot.message_handler(content_types=['photo'])
def get_check(message):
    chat_id = message.chat.id

    if user_step.get(chat_id) == "chek":

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{chat_id}"),
            telebot.types.InlineKeyboardButton("❌ Bekor", callback_data=f"no_{chat_id}")
        )

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=f"💰 To'lov\nUser: {chat_id}\nKod: {user_scooter_code.get(chat_id)}",
            reply_markup=markup
        )

        bot.send_message(chat_id, "⏳ Tekshirilmoqda...")

# TUGMA BOSILGANDA
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message.chat.id != ADMIN_ID:
        return

    data = call.data

    if data.startswith("ok_"):
        user_id = int(data.split("_")[1])

        user_balance[user_id] += 5000

        bot.send_message(user_id, "✅ To'lov tasdiqlandi!\n🛴 Skuter ochildi!")
        bot.answer_callback_query(call.id, "Tasdiqlandi")

    elif data.startswith("no_"):
        user_id = int(data.split("_")[1])

        bot.send_message(user_id, "❌ To'lov bekor qilindi")
        bot.answer_callback_query(call.id, "Bekor qilindi")

bot.infinity_polling()
