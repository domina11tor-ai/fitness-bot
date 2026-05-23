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

def get_user_data(user_id):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT xp, weight, level FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    if not data:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        data = (0, 0, 1)
    conn.close()
    return data

def add_xp(user_id, amount):
    xp, weight, level = get_user_data(user_id)
    new_xp = xp + amount
    new_lvl = 1 + (new_xp // 100)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_lvl, user_id))
    conn.commit()
    conn.close()

# --- ДАННЫЕ ---
DAY_NAMES = {"mon": "ПН", "tue": "ВТ", "wed": "СР", "thu": "ЧТ", "fri": "ПТ", "sat": "СБ", "sun": "ВС"}
EXERCISES = {
    "mon": ["Отжимания 4х20", "Жим гантелей 4х15", "Узкие отжимания 4х15"],
    "tue": ["Тяга гантели 4х15", "Молотки 4х15", "Бицепс классика 4х15"],
    "wed": ["Приседания 4х20", "Болгарские приседания 4х15", "Планка 4х1 мин"],
    "thu": ["Жим вверх 4х12", "Махи в стороны 4х15", "Обратные отжимания 4х15"],
    "fri": ["Становая тяга 4х15", "Тяга 1 рукой 4х15", "Конц. бицепс 4х15"],
    "sat": ["Широкие отжимания 4х20", "Кубковые приседания 4х20", "Икры 4х20"],
    "sun": ["Отдых: Растяжка + Прогулка"]
}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="📊 Статистика", callback_data="show_stats")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Fitness Pro готов! Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "start_workout")
async def workout_days(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for code, name in DAY_NAMES.items():
        kb.button(text=name, callback_data=f"day_{code}")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(4, 3, 1)
    await call.message.edit_text("📅 Выбери день недели:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("day_"))
async def workout_ex(call: types.CallbackQuery):
    day = call.data.split("_")[1]
    kb = InlineKeyboardBuilder()
    for i, ex in enumerate(EXERCISES[day]):
        kb.button(text=ex, callback_data=f"ex_{day}_{i}")
    kb.button(text="⬅️ Назад", callback_data="start_workout")
    kb.adjust(1)
    await call.message.edit_text(f"🏋️ Упражнения на {DAY_NAMES[day]}:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("ex_"))
async def set_timer(call: types.CallbackQuery):
    data = call.data.split("_")
    day, idx = data[1], data[2]
    kb = InlineKeyboardBuilder()
    kb.button(text="⏱ 30 сек", callback_data=f"run_30_{day}_{idx}")
    kb.button(text="⏱ 40 сек", callback_data=f"run_40_{day}_{idx}")
    kb.button(text="⬅️ Назад", callback_data=f"day_{day}")
    kb.adjust(2, 1)
    await call.message.edit_text(f"Подход: {EXERCISES[day][int(idx)]}\nСколько отдыхаем?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("run_"))
async def run_timer(call: types.CallbackQuery):
    data = call.data.split("_")
    sec, day, idx = int(data[1]), data[2], data[3]
    add_xp(call.from_user.id, 25) 
    
    msg = await call.message.edit_text(f"⏳ Отдых: {sec} сек...")
    for i in range(sec - 5, 0, -5):
        await asyncio.sleep(5)
        await msg.edit_text(f"⏳ Отдых: {i} сек...")
    
    # После таймера отправляем новое сообщение с упражнениями
    await call.message.answer("💪 Время вышло! Пора за работу!")
    
    # Создаем клавиатуру заново для возврата
    kb = InlineKeyboardBuilder()
    for i, ex in enumerate(EXERCISES[day]):
        kb.button(text=ex, callback_data=f"ex_{day}_{i}")
    kb.button(text="⬅️ Назад", callback_data="start_workout")
    kb.adjust(1)
    await call.message.answer(f"🏋️ Упражнения на {DAY_NAMES[day]}:", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "weight_menu")
async def weight_prompt(call: types.CallbackQuery):
    await call.message.edit_text("Введите ваш вес (число, например 78.5):")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def weight_save(msg: types.Message):
    w = float(msg.text)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET weight = ? WHERE user_id = ?", (w, msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer(f"✅ Вес {w} кг сохранен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "show_stats")
async def stats(call: types.CallbackQuery):
    xp, w, lvl = get_user_data(call.from_user.id)
    await call.message.edit_text(f"📊 СТАТИСТИКА:\nУровень: {lvl}\nОпыт: {xp} XP\nВес: {w} кг", reply_markup=get_main_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

# --- SERVER ---
async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
