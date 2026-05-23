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

# 2. СРАЗУ СОЗДАЕМ ОБЪЕКТЫ (это то, что вызывало ошибку)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 3. Теперь можно инициализировать БД и прочее
def init_db():
    # ... твой код БД ...
    pass

init_db()

# 4. И только потом декораторы
@dp.message(Command("start"))
async def start(msg: types.Message):
    # ...
