import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище статистики
user_stats = {}

DAY_NAMES = {
    "day_mon": "Понедельник",
    "day_wed": "Среда",
    "day_fri": "Пятница"
}

# Словарь с привязкой упражнений к конкретным дням
EXERCISES_BY_DAY = {
    "day_mon": {"push": "Отжимания", "abs": "Пресс"},
    "day_wed": {"squat": "Приседания", "lunge": "Выпады"},
    "day_fri": {"push": "Отжимания", "plank": "Планка"}
}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 НАЧАТЬ ТРЕНИРОВКУ", callback_data="start_workout")
    kb.button(text="📊 Моя статистика", callback_data="show_stats")
    kb.button(text="🔄 Сбросить статистику", callback_data="reset")
    kb.adjust(1)
    return kb.as_markup()

def get_days_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Понедельник", callback_data="workout_day_mon")
    kb.button(text="Среда", callback_data="workout_day_wed")
    kb.button(text="Пятница", callback_data="workout_day_fri")
    kb.button(text="⬅️ Главное меню", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

def get_exercises_kb(day_key):
    kb = InlineKeyboardBuilder()
    exercises = EXERCISES_BY_DAY.get(day_key, {})
    for ex_id, ex_name in exercises.items():
        kb.button(text=ex_name, callback_data=f"run_ex_{ex_id}_{day_key}")
        
    kb.button(text="🏁 Завершить тренировку", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()


# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

# 1. Нажали Начать тренировку
@dp.callback_query(F.data == "start_workout")
async def start_w(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выбери день недели для тренировки:", reply_markup=get_days_kb())

# 2. Выбрали день -> Показываем план
@dp.callback_query(F.data.startswith("workout_day_"))
async def show_day_plan(call: types.CallbackQuery):
    await call.answer()
    day_key = call.data.replace("workout_", "")
    
    plans = {
        "day_mon": "📅 План на ПОНЕДЕЛЬНИК:\n- Отжимания: 3х15\n- Пресс: 3х20",
        "day_wed": "📅 План на СРЕДУ:\n- Приседания: 3х20\n- Выпады: 3х12",
        "day_fri": "📅 План на ПЯТНИЦУ:\n- Отжимания: 4х12\n- Планка: 3х45 сек"
    }
    
    text = plans.get(day_key, "План не найден.")
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🏋️ Начать упражнения", callback_data=f"start_ex_{day_key}")
    kb.button(text="⬅️ Назад к дням", callback_data="start_workout")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

# 3. Нажали "Начать упраж
