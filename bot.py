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

# --- БАЗА ДАННЫХ И УПРАЖНЕНИЯ ---
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, weight REAL DEFAULT 0)""")
    conn.commit()
    conn.close()

init_db()

# Список упражнений по дням
EXERCISES = {
    "mon": ["Отжимания", "Жим гантелей"],
    "tue": ["Приседания", "Выпады"],
    "wed": ["Планка", "Скручивания"],
}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Fitness Pro готов! Выбери действие:", reply_markup=get_main_kb())

# 1. Выбор дня
@dp.callback_query(F.data == "start_workout")
async def workout_days(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for day_code in EXERCISES.keys():
        kb.button(text=day_code.upper(), callback_data=f"day_{day_code}")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    await call.message.edit_text("📅 Выбери день недели:", reply_markup=kb.as_markup())

# 2. Выбор упражнения конкретного дня
@dp.callback_query(F.data.startswith("day_"))
async def show_exercises(call: types.CallbackQuery):
    day = call.data.split("_")[1]
    kb = InlineKeyboardBuilder()
    for ex in EXERCISES[day]:
        kb.button(text=ex, callback_data="none") # Пока просто текст
    kb.button(text="⬅️ Назад", callback_data="start_workout")
    kb.adjust(1)
    await call.message.edit_text(f"🏋️ Упражнения на {day.upper()}:", reply_markup=kb.as_markup())

# --- УТИЛИТЫ ---
@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def get_motivation(call: types.CallbackQuery):
    await call.answer(random.choice(["Двигайся!", "Ты сможешь!"]), show_alert=True)

# --- ЗАПУСК ---
async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
