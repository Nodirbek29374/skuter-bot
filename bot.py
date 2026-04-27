import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot ishlayapti ✅")


@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text

    if text == "Balance":
        bot.send_message(message.chat.id, "Sizning balans: 0 so'm 💰")

    elif text == "Top Up":
        bot.send_message(message.chat.id, "Pul qo‘shish uchun: Click / Payme link")

    elif text == "Scooters Map":
        bot.send_message(message.chat.id, "📍 Skuterlar xaritasi")

    elif text == "Find Nearest":
        bot.send_message(message.chat.id, "📍 Eng yaqin skuter qidirilmoqda...")

    elif text == "End Ride":
        bot.send_message(message.chat.id, "⛔ Ride tugatildi")

    elif text == "Help":
        bot.send_message(message.chat.id, "Yordam: tugmalardan foydalaning")

    else:
        bot.send_message(message.chat.id, "Noma'lum buyruq ❗")
