import asyncio
import sqlite3
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Инициализация
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

# --- КЛАВИАТУРА ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="🎮 Игра", callback_data="start_game")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Я твой тренер. Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def get_motivation(call: types.CallbackQuery):
    quotes = ["Боль — это временно!", "Ты можешь больше, чем думаешь!", "Дисциплина — ключ к успеху."]
    await call.answer(random.choice(quotes), show_alert=True)

@dp.callback_query(F.data == "start_game")
async def start_game(call: types.CallbackQuery):
    await call.message.edit_text("Игра: Я загадал число от 1 до 5. Угадай! (жми кнопку)", reply_markup=InlineKeyboardBuilder().button(text="1", callback_data="guess_1").button(text="2", callback_data="guess_2").button(text="3", callback_data="guess_3").button(text="4", callback_data="guess_4").button(text="5", callback_data="guess_5").as_markup())

@dp.callback_query(F.data.startswith("guess_"))
async def check_guess(call: types.CallbackQuery):
    target = random.randint(1, 5)
    guess = int(call.data.split("_")[1])
    if guess == target:
        await call.answer("Победа! +50 XP", show_alert=True)
    else:
        await call.answer(f"Не угадал, было {target}", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
