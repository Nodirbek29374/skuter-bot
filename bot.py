import telebot
from telebot.types import ReplyKeyboardMarkup
import sqlite3, time, threading, base64, os
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 ENV yuklash
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not OPENAI_KEY:
    raise Exception("OPENAI_KEY topilmadi (.env tekshir)")

client = OpenAI(api_key=OPENAI_KEY)

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"
bot = telebot.TeleBot(TOKEN)

# DB
conn = sqlite3.connect("skuter.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS rides (user_id INTEGER, active INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS skuters (skuter_id TEXT PRIMARY KEY, code TEXT, status TEXT, lat REAL, lon REAL)")
conn.commit()

SKUTER_PRICE = 5000
PRICE_PER_MIN = 500

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
def get_balance(uid):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    if r: return r[0]
    cursor.execute("INSERT INTO users VALUES (?,0)", (uid,))
    conn.commit()
    return 0

def update_balance(uid, amount):
    bal = get_balance(uid) + amount
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (bal, uid))
    conn.commit()
    return bal

# RIDE
def start_ride_db(uid):
    cursor.execute("DELETE FROM rides WHERE user_id=?", (uid,))
    cursor.execute("INSERT INTO rides VALUES (?,1)", (uid,))
    conn.commit()

def stop_ride_db(uid):
    cursor.execute("UPDATE rides SET active=0 WHERE user_id=?", (uid,))
    conn.commit()

def is_riding(uid):
    cursor.execute("SELECT active FROM rides WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    return r and r[0] == 1

# SKUTER
def add_skuter(sid, code, lat, lon):
    cursor.execute("INSERT OR IGNORE INTO skuters VALUES (?,?,?,?,?)", (sid, code, "free", lat, lon))
    conn.commit()

def get_skuter_by_code(code):
    cursor.execute("SELECT skuter_id, status FROM skuters WHERE code=?", (code,))
    return cursor.fetchone()

def set_skuter_status(sid, st):
    cursor.execute("UPDATE skuters SET status=? WHERE skuter_id=?", (st, sid))
    conn.commit()

def get_all_skuters():
    cursor.execute("SELECT skuter_id, status, lat, lon FROM skuters")
    return cursor.fetchall()

# 🤖 AI CHECK
def ai_check(image_base64):
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu rasmda elektr skuter bormi? faqat yes yoki no"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }]
        )
        return "yes" in resp.choices[0].message.content.lower()
    except Exception as e:
        print("AI error:", e)
        return False

# ⏱ REALTIME
def ride_worker(uid, chat_id):
    bot.send_message(chat_id, "🚀 Skuter harakatda!")
    while True:
        time.sleep(10)  # test (keyin 60 qil)
        if not is_riding(uid):
            break

        bal = get_balance(uid)
        new_bal = bal - PRICE_PER_MIN

        if new_bal <= 0:
            stop_ride_db(uid)
            cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (uid,))
            conn.commit()
            sid = ride_data[uid]["skuter_id"]
            set_skuter_status(sid, "free")
            bot.send_message(chat_id, "❌ Balans tugadi!\n🛑 Skuter yopildi")
            break
        else:
            cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, uid))
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
    b = update_balance(msg.from_user.id, 5000)
    bot.send_message(msg.chat.id, f"✅ +5000\n💰 {b}")

# XARITA
@bot.message_handler(func=lambda m: m.text == "📍 Skuterlar")
def map_(msg):
    for s in get_all_skuters():
        sid, st, lat, lon = s
        txt = "🟢 Bo‘sh" if st=="free" else "🔴 Band"
        bot.send_location(msg.chat.id, lat, lon)
        bot.send_message(msg.chat.id, f"{sid}\n{txt}")

# OLISH
@bot.message_handler(func=lambda m: m.text == "🛴 Skuter olish")
def olish(msg):
    bot.send_message(msg.chat.id, "Kod kiriting yoki QR")

# YOPISH (FIX + FOTO)
@bot.message_handler(func=lambda m: m.text == "🛑 Skuter yopish")
def stop(msg):
    uid = msg.from_user.id
    if not is_riding(uid):
        bot.send_message(msg.chat.id, "❗ Minmayapsiz")
        return

    sid = ride_data[uid]["skuter_id"]
    stop_ride_db(uid)
    set_skuter_status(sid, "free")

    waiting_photo[uid] = sid
    bot.send_message(msg.chat.id, f"🛑 {sid} yopildi\n📸 Rasm yuboring")

# FOTO + AI
@bot.message_handler(content_types=['photo'])
def photo(msg):
    uid = msg.from_user.id
    if uid in waiting_photo:
        sid = waiting_photo[uid]
        bot.send_message(msg.chat.id, "🤖 Tekshiryapman...")

        file = bot.get_file(msg.photo[-1].file_id)
        data = bot.download_file(file.file_path)
        img = base64.b64encode(data).decode()

        if ai_check(img):
            bot.send_message(msg.chat.id, f"✅ AI tasdiqladi\n🛴 {sid}")
            del waiting_photo[uid]
        else:
            bot.send_message(msg.chat.id, "❌ Noto‘g‘ri rasm, qayta yubor")

# HANDLE (oxirida)
@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.from_user.id
    chat_id = msg.chat.id
    text = msg.text

    sk = get_skuter_by_code(text)
    if sk:
        sid, st = sk
        if st != "free":
            bot.send_message(chat_id, "❌ Band")
            return
        if get_balance(uid) < SKUTER_PRICE:
            bot.send_message(chat_id, "❌ Pul yo‘q")
            return

        update_balance(uid, -SKUTER_PRICE)
        start_ride_db(uid)
        set_skuter_status(sid, "busy")

        ride_data[uid] = {"skuter_id": sid}
        threading.Thread(target=ride_worker, args=(uid, chat_id), daemon=True).start()

        bot.send_message(chat_id, f"✅ {sid} ochildi\n🚀 Ishga tushdi\n💰 {get_balance(uid)}")

# SKUTERLAR
add_skuter("SKUTER_1", "A123", 41.3111, 69.2797)
add_skuter("SKUTER_2", "B456", 41.3125, 69.2810)
add_skuter("SKUTER_3", "C789", 41.3130, 69.2750)

print("BOT STARTED")
bot.infinity_polling()
