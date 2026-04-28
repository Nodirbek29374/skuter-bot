import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import time
import threading

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
bot = telebot.TeleBot(TOKEN)

# 🧠 DATABASE
conn = sqlite3.connect("skuter.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rides (
    user_id INTEGER,
    active INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS skuters (
    skuter_id TEXT PRIMARY KEY,
    code TEXT,
    status TEXT,
    lat REAL,
    lon REAL
)
""")

conn.commit()

# ⚙️ SETTINGS
SKUTER_PRICE = 5000
PRICE_PER_MIN = 500
KARTA = "8600 1234 5678 9012"

# 🔘 MENU
def menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛴 Skuter olish"))
    kb.add(KeyboardButton("🛑 Skuter yopish"))
    kb.add(KeyboardButton("📍 Skuterlar"))
    kb.add(KeyboardButton("➕ Pul qo‘shish"))
    kb.add(KeyboardButton("💰 Balans"))
    return kb

# 💰 BALANS
def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0

def update_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (bal, user_id))
    conn.commit()
    return bal

# 🛴 RIDE
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

# 🛴 SKUTER
def add_skuter(skuter_id, code, lat, lon):
    cursor.execute(
        "INSERT OR IGNORE INTO skuters VALUES (?, ?, ?, ?, ?)",
        (skuter_id, code, "free", lat, lon)
    )
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

# 🚀 REALTIME
ride_data = {}

def ride_worker(user_id, chat_id):
    while True:
        time.sleep(60)

        if not is_riding(user_id):
            break

        bal = get_balance(user_id) - PRICE_PER_MIN

        if bal <= 0:
            stop_ride_db(user_id)
            cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
            conn.commit()

            skuter_id = ride_data[user_id]["skuter_id"]
            set_skuter_status(skuter_id, "free")

            bot.send_message(chat_id, "❌ Balans tugadi!\n🛑 Skuter yopildi")
            break
        else:
            cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (bal, user_id))
            conn.commit()

# 🚀 START
@bot.message_handler(commands=['start'])
def start(msg):
    get_balance(msg.from_user.id)
    bot.send_message(msg.chat.id, "🚀 Xush kelibsiz!", reply_markup=menu())

# 💰 BALANS
@bot.message_handler(func=lambda m: m.text == "💰 Balans")
def balans(msg):
    bot.send_message(msg.chat.id, f"💰 Balans: {get_balance(msg.from_user.id)} so‘m")

# ➕ PUL
@bot.message_handler(func=lambda m: m.text == "➕ Pul qo‘shish")
def add_money(msg):
    bal = update_balance(msg.from_user.id, 5000)
    bot.send_message(msg.chat.id,
    f"""✅ 5000 so‘m qo‘shildi
💰 Balans: {bal}

💳 To‘lov:
{KARTA}""")

# 📍 SKUTERLAR XARITADA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar")
def show_map(msg):
    skuters = get_all_skuters()

    for skuter in skuters:
        skuter_id, status, lat, lon = skuter
        status_text = "🟢 Bo‘sh" if status == "free" else "🔴 Band"

        bot.send_location(msg.chat.id, lat, lon)
        bot.send_message(msg.chat.id, f"{skuter_id}\n{status_text}")

# 🛴 SKUTER OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def skuter(msg):
    bot.send_message(msg.chat.id, "📸 QR skaner qiling yoki kodni kiriting:")

# 🔑 ASOSIY LOGIKA
@bot.message_handler(func=lambda m: True)
def handle(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    text = msg.text

    skuter = get_skuter_by_code(text)

    if skuter:
        skuter_id, status = skuter

        if status != "free":
            bot.send_message(chat_id, "❌ Bu skuter band!")
            return

        bal = get_balance(user_id)

        if bal < SKUTER_PRICE:
            bot.send_message(chat_id,
            f"""❌ Balans yetarli emas!

💳 Karta:
{KARTA}""")
            return

        update_balance(user_id, -SKUTER_PRICE)
        start_ride_db(user_id)
        set_skuter_status(skuter_id, "busy")

        ride_data[user_id] = {"skuter_id": skuter_id}

        threading.Thread(target=ride_worker, args=(user_id, chat_id)).start()

        bot.send_message(chat_id,
        f"""✅ {skuter_id} ochildi! 🛴

💰 Balans: {get_balance(user_id)}
⛔ Tugatish: "Skuter yopish" """)

# 🛑 YOPISH
@bot.message_handler(func=lambda m: m.text == "🛑 Skuter yopish")
def stop(msg):
    user_id = msg.from_user.id

    if not is_riding(user_id):
        bot.send_message(msg.chat.id, "❗ Siz minmayapsiz")
        return

    skuter_id = ride_data[user_id]["skuter_id"]

    stop_ride_db(user_id)
    set_skuter_status(skuter_id, "free")

    bot.send_message(msg.chat.id,
    f"""🛑 {skuter_id} yopildi!

💰 Qoldiq: {get_balance(user_id)} so‘m""")

# ▶️ SKUTERLARNI QO‘SH (MISOL)
add_skuter("SKUTER_1", "A123", 41.3111, 69.2797)
add_skuter("SKUTER_2", "B456", 41.3125, 69.2810)
add_skuter("SKUTER_3", "C789", 41.3130, 69.2750)

# ▶️ RUN
bot.infinity_polling()
