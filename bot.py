import asyncio
import sqlite3
import random
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Логирование для отладки
logging.basicConfig(level=logging.INFO)

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
    await call.answer()
    await call.message.edit_text("🏋️ Раздел тренировок. Иди к цели!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "game_guess")
async def game_start(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("🎲 Я загадал число. Угадай (от 1 до 10):", reply_markup=get_main_kb())

@dp.callback_query(F.data == "weight_menu")
async def weight_prompt(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Введите ваш вес (например: 75.5):")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def save_weight(msg: types.Message):
    # Сохранение веса в БД
    weight = float(msg.text)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (msg.from_user.id,))
    cursor.execute("UPDATE users SET weight = ? WHERE user_id = ?", (weight, msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer(f"✅ Вес {weight} кг записан!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def get_motivation(call: types.CallbackQuery):
    quotes = ["Боль — это временно!", "Ты машина!", "Дисциплина — всё!"]
    await call.answer(random.choice(quotes), show_alert=True)

# --- ЗАПУСК ---
async def main():
    # Удаляем вебхуки, чтобы Polling работал без конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен в режиме Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
