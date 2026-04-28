import telebot
import time
import threading

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
ADMIN_ID = 8133027931
CARD = "8600 1234 5678 9012"

bot = telebot.TeleBot(TOKEN)

user_step = {}
user_balance = {}
user_scooter_code = {}
user_time = {}
active_users = {}
user_timer_message = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛴 Skuterni ochish", "💰 Balans")
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    bot.send_message(message.chat.id, f"💰 Balans: {user_balance.get(message.chat.id,0)} so'm")

# SKUTER OCHISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuterni ochish")
def open_scooter(message):
    bot.send_message(message.chat.id, "🔢 Skuter kodini kiriting:")
    user_step[message.chat.id] = "kod"

# KOD
@bot.message_handler(func=lambda m: user_step.get(m.chat.id) == "kod")
def get_code(message):
    chat_id = message.chat.id

    user_scooter_code[chat_id] = message.text

    bot.send_message(chat_id,
        f"💳 Pul tashlang:\n{CARD}\n\n📸 Chek yuboring:")
    user_step[chat_id] = "chek"

# CHEK
@bot.message_handler(content_types=['photo'])
def get_check(message):
    chat_id = message.chat.id

    if user_step.get(chat_id) == "chek":

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{chat_id}"),
            telebot.types.InlineKeyboardButton("❌ Bekor", callback_data=f"no_{chat_id}")
        )

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=f"💰 To'lov\nUser: {chat_id}\nKod: {user_scooter_code.get(chat_id)}",
            reply_markup=markup
        )

        bot.send_message(chat_id, "⏳ Tekshirilmoqda...")

# CALLBACK
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.message.chat.id != ADMIN_ID:
        return

    data = call.data

    # TASDIQLASH
    if data.startswith("confirm_"):
        user_id = int(data.split("_")[1])

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("10 min", callback_data=f"time_{user_id}_10"),
            telebot.types.InlineKeyboardButton("20 min", callback_data=f"time_{user_id}_20"),
        )
        markup.add(
            telebot.types.InlineKeyboardButton("30 min", callback_data=f"time_{user_id}_30"),
            telebot.types.InlineKeyboardButton("1 soat", callback_data=f"time_{user_id}_60"),
        )
        markup.add(
            telebot.types.InlineKeyboardButton("1.5 soat", callback_data=f"time_{user_id}_90"),
            telebot.types.InlineKeyboardButton("2 soat", callback_data=f"time_{user_id}_120"),
        )

        bot.send_message(ADMIN_ID, "⏱ Vaqtni tanlang:", reply_markup=markup)

    # VAQT TANLANDI
    elif data.startswith("time_"):
        parts = data.split("_")
        user_id = int(parts[1])
        minutes = int(parts[2])

        seconds = minutes * 60

        user_time[user_id] = seconds
        active_users[user_id] = True

        msg = bot.send_message(user_id, f"⏱ Qolgan vaqt: {minutes:02d}:00")
        user_timer_message[user_id] = msg.message_id

        threading.Thread(target=countdown, args=(user_id,)).start()

        bot.answer_callback_query(call.id, "Vaqt berildi")

    # BEKOR
    elif data.startswith("no_"):
        user_id = int(data.split("_")[1])
        bot.send_message(user_id, "❌ To'lov bekor qilindi")


# COUNTDOWN (EDIT BILAN)
def countdown(chat_id):
    while active_users.get(chat_id) and user_time.get(chat_id, 0) > 0:

        total = user_time[chat_id]
        mins = total // 60
        secs = total % 60

        time_text = f"{mins:02d}:{secs:02d}"

        try:
            bot.edit_message_text(
                f"⏱ Qolgan vaqt: {time_text}",
                chat_id,
                user_timer_message[chat_id]
            )
        except:
            pass

        time.sleep(1)
        user_time[chat_id] -= 1

    if user_time.get(chat_id, 0) <= 0:
        bot.send_message(chat_id, "❌ Vaqt tugadi! Skuter yopildi")
        active_users[chat_id] = False


print("Bot ishlayapti...")
bot.infinity_polling()
