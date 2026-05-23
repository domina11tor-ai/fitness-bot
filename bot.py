import asyncio
import sqlite3
import random
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Включаем логирование, чтобы видеть нажатия кнопок в консоли Render
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="🎲 Игра", callback_data="start_game")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Бот запущен! Выбери действие:", reply_markup=get_main_kb())

# Прямое указание F.data гарантирует реакцию на кнопку
@dp.callback_query(F.data == "start_workout")
async def workout_handler(call: types.CallbackQuery):
    await call.answer("Открываю тренировки...") # Убирает "часики" на кнопке
    await call.message.edit_text("🏋️ Раздел тренировок!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "start_game")
async def game_handler(call: types.CallbackQuery):
    await call.answer("Открываю игру...")
    await call.message.edit_text("🎮 Угадай число!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "weight_menu")
async def weight_handler(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Введите ваш вес:")

@dp.callback_query(F.data == "get_motivation")
async def motivation_handler(call: types.CallbackQuery):
    await call.answer(random.choice(["Двигайся!", "Ты сможешь!"]), show_alert=True)

# --- ЗАПУСК ---
async def main():
    # Настройка Web-сервера для Render
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # Запуск бота
    print("Бот запущен и ждет нажатий...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
