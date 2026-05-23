import asyncio
import sqlite3
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- ИНИЦИАЛИЗАЦИЯ ---
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, weight REAL DEFAULT 0, level INTEGER DEFAULT 1)""")
    conn.commit()
    conn.close()

init_db()

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="🎲 Игра", callback_data="game_guess")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Fitness Pro готов! Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "start_workout")
async def workout_menu(call: types.CallbackQuery):
    await call.message.edit_text("🏋️ Раздел тренировок. Выберите день:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "game_guess")
async def game_start(call: types.CallbackQuery):
    await call.message.edit_text("🎲 Я загадал число от 1 до 10. Угадай:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "weight_menu")
async def weight_prompt(call: types.CallbackQuery):
    await call.message.edit_text("Введите ваш вес в чат:")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def save_weight(msg: types.Message):
    await msg.answer("✅ Вес сохранен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def get_motivation(call: types.CallbackQuery):
    await call.answer(random.choice(["Боль — это временно!", "Ты машина!"]), show_alert=True)

# --- УНИВЕРСАЛЬНЫЙ ТАЙМЕР ---
@dp.callback_query(F.data == "start_timer")
async def run_timer(call: types.CallbackQuery):
    sec = 30
    msg = call.message
    for i in range(sec, 0, -5):
        await msg.edit_text(f"⏳ Отдых: {i} сек...")
        await asyncio.sleep(5)
    
    # ВОЗВРАТ В МЕНЮ ЧЕРЕЗ РЕДАКТИРОВАНИЕ
    await msg.edit_text("💪 Время вышло! Пора работать!", reply_markup=get_main_kb())

# --- ЗАПУСК ---
async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
