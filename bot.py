import sqlite3
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, weight REAL DEFAULT 0, level INTEGER DEFAULT 1)""")
    conn.commit()
    conn.close()

init_db()

def update_user_progress(user_id, xp_gain=10):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    
    if not data:
        cursor.execute("INSERT INTO users (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp_gain, 1))
    else:
        new_xp = data[0] + xp_gain
        new_lvl = 1 + (new_xp // 100) # Уровень за каждые 100 XP
        cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_lvl, user_id))
    conn.commit()
    conn.close()
    return new_lvl

# --- МОТИВАЦИЯ ---
MOTIVATION = [
    "Твое тело может выдержать почти все. Это твой разум должен быть убежден.",
    "Не останавливайся, когда устал. Останавливайся, когда закончил!",
    "Каждая тренировка — это вклад в твое будущее я.",
    "Результаты приходят не сразу, они приходят с постоянством."
]

# --- КЛАВИАТУРА ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка (XP+)", callback_data="start_workout")
    kb.button(text="⚖️ Записать вес", callback_data="weight_set")
    kb.button(text="📊 Статистика/Уровень", callback_data="show_stats")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(f"Привет! {random.choice(MOTIVATION)}", reply_markup=get_main_kb())

@dp.callback_query(F.data == "get_motivation")
async def show_motivation(call: types.CallbackQuery):
    await call.answer(random.choice(MOTIVATION), show_alert=True)

@dp.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT xp, weight, level FROM users WHERE user_id = ?", (call.message.chat.id,))
    data = cursor.fetchone()
    conn.close()
    
    if data:
        await call.message.edit_text(f"📊 Твой прогресс:\nУровень: {data[2]}\nОпыт: {data[0]} XP\nПоследний вес: {data[1]} кг", reply_markup=get_main_kb())
    else:
        await call.answer("Данных еще нет!")

@dp.callback_query(F.data == "start_workout")
async def workout(call: types.CallbackQuery):
    new_lvl = update_user_progress(call.message.chat.id, 20)
    await call.answer(f"Тренировка засчитана! +20 XP. Твой уровень: {new_lvl}", show_alert=True)
    await call.message.edit_text("Выбери упражнение:", reply_markup=get_main_kb())

# (Остальной код тренировок можно интегрировать сюда)
