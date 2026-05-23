import asyncio
import sqlite3
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ---
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

init_db()

# --- КЛАВИАТУРА МЕНЮ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="list_days")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="🎮 Игра", callback_data="start_game")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ЛОГИКА ТРЕНИРОВОК ---
@dp.callback_query(F.data == "list_days")
async def list_days(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    days = {"ПН": "day_mon", "ВТ": "day_tue", "СР": "day_wed"} # Добавьте остальные по аналогии
    for name, code in days.items():
        kb.button(text=name, callback_data=code)
    await call.message.edit_text("🏋️ Выбери день недели:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("day_"))
async def show_exercises(call: types.CallbackQuery):
    # Здесь будем выводить список упражнений для выбранного дня
    await call.message.edit_text("Список упражнений: \n1. Отжимания\n2. Приседания\n(в разработке)")

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Выбери действие:", reply_markup=get_main_kb())

# --- ЗАПУСК ---
async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
