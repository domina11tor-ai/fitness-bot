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

# Глобальный словарь для отслеживания текущего упражнения пользователя
user_progress = {}

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
    "mon": ["Отжимания", "Жим гантелей", "Узкие отжимания"],
    "tue": ["Тяга гантели", "Молотки", "Бицепс"],
    "wed": ["Приседания", "Болгарские приседания", "Планка"],
    "thu": ["Жим вверх", "Махи в стороны", "Обратные отжимания"],
    "fri": ["Становая тяга", "Тяга 1 рукой", "Конц. бицепс"],
    "sat": ["Широкие отжимания", "Кубковые приседания", "Икры"],
    "sun": ["Отдых: Растяжка"]
}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="📊 Статистика", callback_data="show_stats")
    kb.button(text="🎲 Угадай число", callback_data="game_guess")
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
    kb.button(text="⏱ 45 сек", callback_data=f"run_45_{day}_{idx}")
    kb.button(text="⬅️ Назад", callback_data=f"day_{day}")
    kb.adjust(2, 1)
    await call.message.edit_text(f"Упражнение: {EXERCISES[day][int(idx)]}\nСколько отдыхаем?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("run_"))
async def run_timer(call: types.CallbackQuery):
    data = call.data.split("_")
    sec, day, idx = int(data[1]), data[2], data[3]
    user_progress[call.from_user.id] = f"{day}_{idx}" # Запоминаем упражнение
    
    msg = await call.message.edit_text(f"⏳ Отдых: {sec} сек...")
    for i in range(sec - 5, 0, -5):
        await asyncio.sleep(5)
        await msg.edit_text(f"⏳ Отдых: {i} сек...")
    
    await call.message.answer(f"💪 Время вышло! Введите количество повторений для {EXERCISES[day][int(idx)]}:")

@dp.message(F.text.regexp(r'^\d+$'))
async def save_reps(msg: types.Message):
    if msg.from_user.id not in user_progress:
        await msg.answer("Сначала выберите упражнение в меню тренировок!")
        return
        
    reps = int(msg.text)
    xp_gain = reps * 2
    add_xp(msg.from_user.id, xp_gain)
    del user_progress[msg.from_user.id] # Очистка прогресса
    
    await msg.answer(f"✅ Записано: {reps} повт. (+{xp_gain} XP)!", reply_markup=get_main_kb())

# --- ИГРА ---
@dp.callback_query(F.data == "game_guess")
async def game_guess_start(call: types.CallbackQuery):
    secret = random.randint(1, 10)
    kb = InlineKeyboardBuilder()
    for i in range(1, 11):
        kb.button(text=str(i), callback_data=f"check_{i}_{secret}")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(5, 5, 1)
    await call.message.edit_text("🎲 Угадай число от 1 до 10:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("check_"))
async def check_guess(call: types.CallbackQuery):
    guess, secret = map(int, call.data.split("_")[1:])
    if guess == secret:
        add_xp(call.from_user.id, 100)
        await call.answer("🎉 Правильно! +100 XP", show_alert=True)
    else:
        await call.answer(f"❌ Неверно, было {secret}.", show_alert=True)
    await back(call)

# --- УТИЛИТЫ ---
@dp.callback_query(F.data == "weight_menu")
async def weight_prompt(call: types.CallbackQuery):
    await call.message.edit_text("Введите ваш вес (кг):")

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def weight_save(msg: types.Message):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET weight = ? WHERE user_id = ?", (float(msg.text), msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer("✅ Вес сохранен!", reply_markup=get_main_kb())

@dp.callback_query(F.data == "show_stats")
async def stats(call: types.CallbackQuery):
    xp, w, lvl = get_user_data(call.from_user.id)
    await call.message.edit_text(f"📊 СТАТИСТИКА:\nУровень: {lvl}\nОпыт: {xp} XP\nВес: {w} кг", reply_markup=get_main_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
