import asyncio
import sqlite3
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Инициализация бота и диспетчера
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, weight REAL DEFAULT 0, level INTEGER DEFAULT 1)""")
    conn.commit()
    conn.close()

init_db()

# Основное меню
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="🎮 Игра", callback_data="start_game")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# Обработчики сообщений и кнопок
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "start_workout")
async def start_workout(call: types.CallbackQuery):
    await call.answer("Запуск тренировки...")
    await call.message.edit_text("🏋️ Раздел тренировок активен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "weight_menu")
async def weight_menu(call: types.CallbackQuery):
    await call.message.edit_text("Введите ваш текущий вес цифрой (например: 80):")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def save_weight(msg: types.Message):
    weight = float(msg.text)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO users (user_id, weight) VALUES (?, ?)", (msg.from_user.id, weight))
    conn.commit()
    conn.close()
    await msg.answer(f"✅ Вес {weight} кг сохранен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def get_motivation(call: types.CallbackQuery):
    quotes = ["Боль — это временно!", "Дисциплина — ключ к успеху!"]
    await call.answer(random.choice(quotes), show_alert=True)

@dp.callback_query(F.data == "start_game")
async def start_game(call: types.CallbackQuery):
    await call.message.edit_text("Игра: Угадай число от 1 до 3. (кнопки ниже)", reply_markup=InlineKeyboardBuilder().button(text="1", callback_data="g1").button(text="2", callback_data="g2").button(text="3", callback_data="g3").as_markup())

# Запуск бота и сервера
async def main():
    # Сервер для Render
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
