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

# --- БАЗА ДАННЫХ (с новыми полями) ---
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, weight REAL DEFAULT 0, level INTEGER DEFAULT 1)""")
    # Таблица для истории веса
    cursor.execute("""CREATE TABLE IF NOT EXISTS weight_history 
                      (user_id INTEGER, weight REAL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

init_db()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def add_xp(user_id, amount):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + ? WHERE user_id = ?", (amount, user_id))
    # Обновление уровня
    cursor.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
    xp = cursor.fetchone()[0]
    new_lvl = 1 + (xp // 100)
    cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (new_lvl, user_id))
    conn.commit()
    conn.close()

# --- МЕНЮ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="📊 Статистика", callback_data="show_stats")
    kb.button(text="🎮 Игры", callback_data="games_menu")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.button(text="🧠 Факты", callback_data="get_fact")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.callback_query(F.data == "get_motivation")
async def send_motivation(call: types.CallbackQuery):
    quotes = ["Боль временна, гордость вечна!", "Твое тело — твой храм.", "Дисциплина делает то, что нужно, даже когда не хочется."]
    await call.answer(random.choice(quotes), show_alert=True)

@dp.callback_query(F.data == "get_fact")
async def send_fact(call: types.CallbackQuery):
    facts = ["Мышцам нужно 48 часов для восстановления.", "Белок — строительный материал.", "Вода важна для метаболизма."]
    await call.message.answer(f"💡 Факт дня: {random.choice(facts)}", reply_markup=get_main_kb())

# --- ИГРА "УГАДАЙ ЧИСЛО" ---
@dp.callback_query(F.data == "games_menu")
async def games_menu(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Угадай число", callback_data="game_guess")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    await call.message.edit_text("🎮 Выбери игру:", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "game_guess")
async def game_guess(call: types.CallbackQuery):
    secret = random.randint(1, 5)
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(text=str(i), callback_data=f"check_{i}_{secret}")
    await call.message.edit_text("Угадай число от 1 до 5:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("check_"))
async def check_guess(call: types.CallbackQuery):
    guess, secret = map(int, call.data.split("_")[1:])
    if guess == secret:
        add_xp(call.from_user.id, 50)
        await call.answer("🎉 Победа! +50 XP", show_alert=True)
    else:
        await call.answer(f"❌ Неверно, было {secret}", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

# --- ЗАПИСЬ ВЕСА ---
@dp.callback_query(F.data == "weight_menu")
async def weight_menu(call: types.CallbackQuery):
    await call.message.edit_text("Введите ваш вес в кг (например, 80.5):")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def save_weight(msg: types.Message):
    w = float(msg.text)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET weight = ? WHERE user_id = ?", (w, msg.from_user.id))
    cursor.execute("INSERT INTO weight_history (user_id, weight) VALUES (?, ?)", (msg.from_user.id, w))
    conn.commit()
    conn.close()
    await msg.answer("✅ Вес записан в дневник!", reply_markup=get_main_kb())

# --- ЗАПУСК ---
@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
