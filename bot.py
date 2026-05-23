import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище статистики теперь разделено по дням:
# user_stats[chat_id] = {"day_mon": {"ex_push": 0, "ex_squat": 0}, ...}
user_stats = {}

# Вспомогательный словарь для красивых названий дней
DAY_NAMES = {
    "day_mon": "Понедельник",
    "day_wed": "Среда",
    "day_fri": "Пятница"
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
    # Передаем день внутри callback_data, чтобы бот знал, куда засчитать подход
    kb.button(text="Отжимания", callback_data=f"run_ex_push_{day_key}")
    kb.button(text="Приседания", callback_data=f"run_ex_squat_{day_key}")
    kb.button(text="⬅️ К выбору дней", callback_data="start_workout")
    kb.adjust(1)
    return kb.as_markup()


# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Добро пожаловать в тренажер. Выбери действие:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

# 1. НАЖАЛИ "НАЧАТЬ ТРЕНИРОВКУ" -> ПРОВАЛИВАЕМСЯ В ВЫБОР ДНЕЙ
@dp.callback_query(F.data == "start_workout")
async def start_w(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выбери день недели для тренировки:", reply_markup=get_days_kb())

# 2. ВЫБРАЛИ ДЕНЬ -> ПОКАЗЫВАЕМ ПЛАН И КНОПКУ СТАРТА УПРАЖНЕНИЙ
@dp.callback_query(F.data.startswith("workout_day_"))
async def show_day_plan(call: types.CallbackQuery):
    await call.answer()
    day_key = call.data.replace("workout_", "") # получим day_mon, day_wed или day_fri
    
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

# 3. НАЖАЛИ "НАЧАТЬ УПРАЖНЕНИЯ" -> МЕНЮ УПРАЖНЕНИЙ ДЛЯ КОНКРЕТНОГО ДНЯ
@dp.callback_query(F.data.startswith("start_ex_"))
async def start_exercises(call: types.CallbackQuery):
    await call.answer()
    day_key = call.data.replace("start_ex_", "") # получим day_mon и т.д.
    
    await call.message.edit_text(
        f"Выполняем тренировку за {DAY_NAMES.get(day_key)}.\nВыбери упражнение:", 
        reply_markup=get_exercises_kb(day_key)
    )

# 4. ВЫБРАЛИ УПРАЖНЕНИЕ -> ВЫБОР ТАЙМЕРА ОТДЫХА
@dp.callback_query(F.data.startswith("run_ex_"))
async def select_timer(call: types.CallbackQuery):
    await call.answer()
    # Данные выглядят так: run_ex_push_day_mon
    parts = call.data.replace("run_ex_", "").split("_")
    ex_name = parts[0] # push или squat
    day_key = f"{parts[1]}_{parts[2]}" # day_mon / day_wed / day_fri
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 5 сек", callback_data=f"t_5_{ex_name}_{day_key}")
    kb.button(text="Отдых 10 сек", callback_data=f"t_10_{ex_name}_{day_key}")
    kb.button(text="⬅️ Назад", callback_data=f"start_ex_{day_key}")
    kb.adjust(1)
    
    await call.message.edit_text("Подход завершен? Выбери время отдыха:", reply_markup=kb.as_markup())

# 5. ТАЙМЕР И ЗАПИСЬ В СТАТИСТИКУ КОНКРЕТНОГО ДНЯ
@dp.callback_query(F.data.startswith("t_"))
async def run_timer(call: types.CallbackQuery):
    await call.answer()
    
    # Считываем данные (пример: t_5_push_day_mon)
    parts = call.data.split("_")
    seconds = int(parts[1])
    ex_type = f"ex_{parts[2]}" # ex_push или ex_squat
    day_key = f"{parts[3]}_{parts[4]}" # day_mon / day_wed / day_fri
    
    chat_id = call.message.chat.id
    
    # Инициализация словарей статистики
    if chat_id not in user_stats:
        user_stats[chat_id] = {}
    if day_key not in user_stats[chat_id]:
        user_stats[chat_id][day_key] = {"ex_push": 0, "ex_squat": 0}
        
    # Плюсуем подход конкретному дню
    user_stats[chat_id][day_key][ex_type] += 1

    await call.message.edit_text(f"✅ Подход засчитан в {DAY_NAMES.get(day_key)}!\n⏳ Таймер отдыха: {seconds} сек...")
    await asyncio.sleep(seconds)
    
    await call.message.edit_text("✅ Время вышло! Готов к следующему подходу?", reply_markup=get_exercises_kb(day_key))

# ПОКАЗ СТАТИСТИКИ С РАЗБИВКОЙ ПО ДНЯМ
@dp.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery):
    await call.answer()
    chat_id = call.message.chat.id
    
    stats = user_stats.get(chat_id, {})
    
    text = "📊 **Твоя статистика по дням недели:**\n\n"
    
    for day_key, day_name in DAY_NAMES.items():
        day_data = stats.get(day_key, {"ex_push": 0, "ex_squat": 0})
        text += f"🔹 **{day_name}:**\n"
        text += f"   💪 Отжимания: {day_data.get('ex_push', 0)} подх.\n"
        text += f"   🦵 Приседания: {day_data.get('ex_squat', 0)} подх.\n\n"
        
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад в меню", callback_data="back_main")
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery):
    user_stats[call.message.chat.id] = {}
    await call.answer("Вся статистика очищена!", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
