import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import time
import threading
import base64
from openai import OpenAI

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
OPENAI_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# DATABASE
conn = sqlite3.connect("skuter.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS rides (user_id INTEGER, active INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS skuters (skuter_id TEXT PRIMARY KEY, code TEXT, status TEXT, lat REAL, lon REAL)")
conn.commit()

# SETTINGS
SKUTER_PRICE = 5000
PRICE_PER_MIN = 500
KARTA = "8600 1234 5678 9012"

ride_data = {}
waiting_photo = {}

# MENU
def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛴 Skuter olish", "🛑 Skuter yopish")
    kb.add("📍 Skuterlar")
    kb.add("➕ Pul qo‘shish", "💰 Balans")
    return kb

# BALANS
def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO users VALUES (?, ?)", (user_id, 0))
    conn.commit()
    return 0

def update_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (bal, user_id))
    conn.commit()
    return bal

# RIDE
def start_ride_db(user_id):
    cursor.execute("DELETE FROM rides WHERE user_id=?", (user_id,))
    cursor.execute("INSERT INTO rides VALUES (?, ?)", (user_id, 1))
    conn.commit()

def stop_ride_db(user_id):
    cursor.execute("UPDATE rides SET active=0 WHERE user_id=?", (user_id,))
    conn.commit()

def is_riding(user_id):
    cursor.execute("SELECT active FROM rides WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] == 1

# SKUTER
def add_skuter(skuter_id, code, lat, lon):
    cursor.execute("INSERT OR IGNORE INTO skuters VALUES (?, ?, ?, ?, ?)", (skuter_id, code, "free", lat, lon))
    conn.commit()

def get_skuter_by_code(code):
    cursor.execute("SELECT skuter_id, status FROM skuters WHERE code=?", (code,))
    return cursor.fetchone()

def set_skuter_status(skuter_id, status):
    cursor.execute("UPDATE skuters SET status=? WHERE skuter_id=?", (status, skuter_id))
    conn.commit()

def get_all_skuters():
    cursor.execute("SELECT skuter_id, status, lat, lon FROM skuters")
    return cursor.fetchall()

# AI CHECK
def ai_check(image_base64):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Bu rasmda elektr skuter bormi? faqat yes yoki no"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
        )
        return "yes" in response.choices[0].message.content.lower()
    except:
        return False

# REALTIME
def ride_worker(user_id, chat_id):
    bot.send_message(chat_id, "🚀 Skuter harakatda!")

    while True:
        time.sleep(10)  # test

        if not is_riding(user_id):
            break

        bal = get_balance(user_id)
        new_bal = bal - PRICE_PER_MIN

        if new_bal <= 0:
            stop_ride_db(user_id)
            cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
            conn.commit()

            skuter_id = ride_data[user_id]["skuter_id"]
            set_skuter_status(skuter_id, "free")

            bot.send_message(chat_id, "❌ Balans tugadi!\n🛑 Skuter yopildi")
            break
        else:
            cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, user_id))
            conn.commit()

            bot.send_message(chat_id, f"⏱ -{PRICE_PER_MIN}\n💰 {new_bal}")

# START
@bot.message_handler(commands=['start'])
def start(msg):
    get_balance(msg.from_user.id)
    bot.send_message(msg.chat.id, "🚀 Xush kelibsiz", reply_markup=menu())

# BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def bal(msg):
    bot.send_message(msg.chat.id, f"💰 {get_balance(msg.from_user.id)}")

# PUL
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def pul(msg):
    bal = update_balance(msg.from_user.id, 5000)
    bot.send_message(msg.chat.id, f"✅ +5000\n💰 {bal}")

# XARITA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar")
def map(msg):
    for s in get_all_skuters():
        skuter_id, status, lat, lon = s
        txt = "🟢 Bo‘sh" if status=="free" else "🔴 Band"
        bot.send_location(msg.chat.id, lat, lon)
        bot.send_message(msg.chat.id, f"{skuter_id}\n{txt}")

# OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def olish(msg):
    bot.send_message(msg.chat.id, "Kod kiriting yoki QR")

# YOPISH (FIX)
@bot.message_handler(func=lambda m: m.text == "🛑 Skuter yopish")
def stop(msg):
    user_id = msg.from_user.id

    if not is_riding(user_id):
        bot.send_message(msg.chat.id, "❗ Minmayapsiz")
        return

    skuter_id = ride_data[user_id]["skuter_id"]

    stop_ride_db(user_id)
    set_skuter_status(skuter_id, "free")

    waiting_photo[user_id] = skuter_id

    bot.send_message(msg.chat.id, f"🛑 {skuter_id} yopildi\n📸 Rasm yuboring")

# PHOTO + AI
@bot.message_handler(content_types=['photo'])
def photo(msg):
    user_id = msg.from_user.id

    if user_id in waiting_photo:
        skuter_id = waiting_photo[user_id]

        bot.send_message(msg.chat.id, "🤖 Tekshiryapman...")

        file = bot.get_file(msg.photo[-1].file_id)
        data = bot.download_file(file.file_path)
        img = base64.b64encode(data).decode()

        if ai_check(img):
            bot.send_message(msg.chat.id, f"✅ AI tasdiqladi\n🛴 {skuter_id}")
            del waiting_photo[user_id]
        else:
            bot.send_message(msg.chat.id, "❌ Noto‘g‘ri rasm")

# HANDLE (ENG OXIRIDA)
@bot.message_handler(func=lambda m: True)
def handle(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    text = msg.text

    skuter = get_skuter_by_code(text)

    if skuter:
        skuter_id, status = skuter

        if status != "free":
            bot.send_message(chat_id, "❌ Band")
            return

        if get_balance(user_id) < SKUTER_PRICE:
            bot.send_message(chat_id, "❌ Pul yo‘q")
            return

        update_balance(user_id, -SKUTER_PRICE)
        start_ride_db(user_id)
        set_skuter_status(skuter_id, "busy")

        ride_data[user_id] = {"skuter_id": skuter_id}

        threading.Thread(target=ride_worker, args=(user_id, chat_id), daemon=True).start()

        bot.send_message(chat_id,
        f"""✅ {skuter_id} ochildi

🚀 Ishga tushdi
💰 {get_balance(user_id)}""")

# SKUTERLAR
add_skuter("SKUTER_1", "A123", 41.3111, 69.2797)
add_skuter("SKUTER_2", "B456", 41.3125, 69.2810)
add_skuter("SKUTER_3", "C789", 41.3130, 69.2750)

bot.infinity_polling()
