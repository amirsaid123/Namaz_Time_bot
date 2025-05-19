import asyncio
import logging
import os
import sys
import dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BotCommand
from functions import get_districts, get_time_districts
from functions import make_keyboard_button

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token is not found in the .env file")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

CITIES = [
    "Toshkent viloyati", "Buxoro viloyati", "Farg‘ona viloyati", "Sirdaryo viloyati", "Jizzax viloyati",
    "Navoiy viloyati", "Namangan viloyati", "Qoraqalpog‘iston Respublikasi", "Samarqand viloyati",
    "Surxondaryo viloyati", "Qashqadaryo viloyati", "Andijon viloyati", "Xorazm viloyati"
]


@dp.message(Command('start'))
async def start_command(message: Message):
    await message.bot.set_my_commands([
        BotCommand(command="/start", description="Start"),
        BotCommand(command="/help", description="Help")
    ])

    keyboard = await make_keyboard_button(CITIES, [2])
    await message.reply("Assalomu Alaykum! Namoz Vaqti botga Xush kelibsiz!\nIltimos, viloyatingizni tanlang:",
                        reply_markup=keyboard)


@dp.message(F.text.in_(CITIES))
async def city_handler(message: Message):
    if message.text == "Qoraqalpog‘iston Respublikasi":
        city_name = "qoraqalpogistonrespublikasi"
    else:
        city_name = message.text.split()[0]

    districts = await get_districts(city_name)
    if not districts:
        await message.reply("Ushbu hudud uchun ma'lumot topilmadi.")
        return

    districts.append("⬅️ Orqaga")

    keyboard = await make_keyboard_button(districts, [2])
    await message.reply(f"{message.text} viloyati tumani tanlang:", reply_markup=keyboard)


@dp.message()
async def districts_handler(message: Message):
    if message.text == "⬅️ Orqaga":
        keyboard = await make_keyboard_button(CITIES, [2])
        await message.reply("Iltimos, viloyatingizni tanlang:", reply_markup=keyboard)
        return

    district_name = message.text.strip()
    namazs = await get_time_districts(district_name)

    if not namazs:
        await message.reply("Kechirasiz, bu tuman uchun ma'lumot topilmadi.")
        return

    message_text = f"🕌 <b>{district_name} Namoz Vaqtlari</b> 📍\n\n"
    day_info = namazs[0]
    message_text += f"📅 <b>{day_info['Day']}</b>\n━━━━━━━━━━━━━━\n"

    for namaz in namazs[1:]:
        message_text += f"🕋 <b>{namaz['Name']}:</b> {namaz['Time']}\n"

    keyboard = await make_keyboard_button(["⬅️ Orqaga"], [1])
    await message.reply(message_text, parse_mode="HTML", reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
