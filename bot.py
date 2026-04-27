import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = "BOT_TOKEN=8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchi ma'lumotlari
users = {}

# Menu
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("💰 Balans", "➕ Pul qo‘shish")
menu.add("🛴 Haydashni boshlash", "❌ Haydashni tugatish")

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    users[user_id] = {"balans": 10000, "ride": False}
    await msg.answer("Xush kelibsiz!", reply_markup=menu)

@dp.message_handler(lambda m: m.text == "💰 Balans")
async def balans(msg: types.Message):
    user = users.get(msg.from_user.id)
    if user:
        await msg.answer(f"Balans: {user['balans']} so'm")

@dp.message_handler(lambda m: m.text == "➕ Pul qo‘shish")
async def pul(msg: types.Message):
    await msg.answer("Admin bilan bog‘laning")

@dp.message_handler(lambda m: m.text == "🛴 Haydashni boshlash")
async def start_ride(msg: types.Message):
    user = users[msg.from_user.id]
    user["ride"] = True
    await msg.answer("Ride boshlandi!")

    asyncio.create_task(minus_balans(msg.from_user.id))

async def minus_balans(user_id):
    while users[user_id]["ride"]:
        await asyncio.sleep(60)
        users[user_id]["balans"] -= 300

        try:
            await bot.send_message(user_id, f"💸 1 minut o‘tdi\nBalans: {users[user_id]['balans']} so'm")
        except:
            pass

@dp.message_handler(lambda m: m.text == "❌ Haydashni tugatish")
async def stop_ride(msg: types.Message):
    users[msg.from_user.id]["ride"] = False
    await msg.answer("Ride tugadi!")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
