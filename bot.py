import telebot
from telebot import types

TOKEN = "SENING_TOKENING"
bot = telebot.TeleBot(TOKEN)

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("💰 Balans")
    btn2 = types.KeyboardButton("+ Pul qo‘shish")
    btn3 = types.KeyboardButton("🛴 Skuter olish")
    btn4 = types.KeyboardButton("❌ Haydashni tugatish")
    btn5 = types.KeyboardButton("📍 Skuterlar xaritada", request_location=True)

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)

    bot.send_message(message.chat.id, "Kerakli bo‘limni tanlang:", reply_markup=markup)


# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(message):
    bot.send_message(message.chat.id, "Sizning balansingiz: 10 000 so‘m 💵")


# PUL QO‘SHISH
@bot.message_handler(func=lambda m: m.text == "+ Pul qo‘shish")
def pul(message):
    bot.send_message(message.chat.id, "💳 To‘lov uchun Click / Payme ishlating")


# SKUTER OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def skuter(message):
    bot.send_message(message.chat.id, "🛴 Skuter ochildi! Yaxshi haydash!")


# TO‘XTATISH
@bot.message_handler(func=lambda m: m.text == "❌ Haydashni tugatish")
def stop(message):
    bot.send_message(message.chat.id, "🛑 Haydash tugatildi")


# XARITA (LOKATSIYA)
@bot.message_handler(content_types=['location'])
def location(message):
    lat = message.location.latitude
    lon = message.location.longitude

    bot.send_message(message.chat.id, f"📍 Sizning joylashuv:\n{lat}, {lon}")


# DEFAULT (ortiqcha xabarlar uchun)
@bot.message_handler(func=lambda m: True)
def other(message):
    bot.send_message(message.chat.id, "❗ Iltimos pastdagi tugmalardan foydalaning")

bot.polling()
