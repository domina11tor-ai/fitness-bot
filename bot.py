import asyncio
import sqlite3
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# 1. Сначала загружаем токен
TOKEN = os.getenv("BOT_TOKEN")

# 2. СРАЗУ создаем объекты bot и dp
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 3. Функция БД
def init_db():
    # ... твой код инициализации БД ...
    pass

init_db()

# 4. И ТОЛЬКО ПОСЛЕ ЭТОГО пишем обработчики (декораторы)
@dp.message(Command("start"))
async def start(msg: types.Message):
    # ...

@dp.callback_query(F.data == "weight_menu")
async def weight_menu(call: types.CallbackQuery):
    # ...

# 5. И в самом низу запуск
if __name__ == "__main__":
    asyncio.run(main())
