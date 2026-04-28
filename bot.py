from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

TOKEN = "8110986517:AAG3DL1iUHgPv1Zk0mp51p-UB5mrhEsl4M8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📱 DOIMIY MENU
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛴 Skuterni ochish"), KeyboardButton(text="💰 Balans")],
        [KeyboardButton(text="⏱ Vaqt"), KeyboardButton(text="⚙️ Sozlamalar")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False  # MUHIM!
)

# 🚀 START
@dp.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Menyudan foydalaning 👇", reply_markup=menu)

# 🔘 HAR DOIM MENYU QAYTADI
@dp.message()
async def handle(message: types.Message):
    text = message.text

    if text == "🛴 Skuterni ochish":
        await message.answer("Kod kiriting:", reply_markup=menu)

    elif text == "💰 Balans":
        await message.answer("Balans: 0 so‘m", reply_markup=menu)

    elif text == "⏱ Vaqt":
        await message.answer("Vaqt tanlang", reply_markup=menu)

    else:
        await message.answer("Noto‘g‘ri buyruq", reply_markup=menu)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
