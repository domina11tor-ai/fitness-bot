import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен берется из скрытых настроек Render
TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения статистики пользователей
user_stats = {}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 НАЧАТЬ ТРЕНИРОВКУ", callback_data="start_workout")
    kb.button(text="📊 Моя статистика", callback_data="show_stats") # <--- НОВАЯ КНОПКА
    kb.button(text="🔄 Сбросить", callback_data="reset")
    kb.button(text="Понедельник", callback_data="day_mon")
    kb.button(text="Среда", callback_data="day_wed")
    kb.button(text="Пятница", callback_data="day_fri")
    kb.adjust(1)
    return kb.as_markup()

def get_exercises_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="ex_push")
    kb.button(text="Приседания", callback_data="ex_squat")
    kb.button(text="⬅️ В меню", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    # При старте создаем пустую статистику для пользователя, если её еще нет
    if msg.chat.id not in user_stats:
        user_stats[msg.chat.id] = {"ex_push": 0, "ex_squat": 0}
    await msg.answer("Привет! Выбери действие:", reply_markup=get_main_kb())

# ОБРАБОТЧИК ДНЕЙ НЕДЕЛИ
@dp.callback_query(F.data.startswith("day_"))
async def day_handler(call: types.CallbackQuery):
    await call.answer()
    plans = {
        "day_mon": "📅 Понедельник:\n- Отжимания: 3х15\n- Пресс: 3х20",
        "day_wed": "📅 Среда:\n- Приседания: 3х20\n- Выпады: 3х12",
        "day_fri": "📅 Пятница:\n- Отжимания: 4х12\n- Планка: 3х45 сек"
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="back_main")
    await call.message.edit_text(plans.get(call.data, "План не найден."), reply_markup=kb.as_markup())

# ОБРАБОТЧИК СТАТИСТИКИ
@dp.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery):
    await call.answer()
    chat_id = call.message.chat.id
    
    # Получаем статистику, если ее нет - ставим нули
    stats = user_stats.get(chat_id, {"ex_push": 0, "ex_squat": 0})
    
    text = (
        "📊 **Твоя статистика подходов:**\n\n"
        f"💪 Отжимания: {stats.get('ex_push', 0)} подходов\n"
        f"🦵 Приседания: {stats.get('ex_squat', 0)} подходов"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="back_main")
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "start_workout")
async def start_w(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выбери упражнение:", reply_markup=get_exercises_kb())

@dp.callback_query(F.data.startswith("ex_"))
async def select_ex(call: types.CallbackQuery):
    await call.answer()
    ex_name = call.data # Запоминаем, какое упражнение выбрано (например, ex_push)
    
    kb = InlineKeyboardBuilder()
    # Передаем название упражнения прямо в кнопку таймера
    kb.button(text="Отдых 5 сек", callback_data=f"timer_5_{ex_name}")
    kb.button(text="Отдых 10 сек", callback_data=f"timer_10_{ex_name}")
    kb.button(text="⬅️ Назад", callback_data="start_workout")
    kb.adjust(1)
    
    await call.message.edit_text("Подход завершен? Выбери время отдыха:", reply_markup=kb.as_markup())

# ТАЙМЕР И ЗАПИСЬ СТАТИСТИКИ
@dp.callback_query(F.data.startswith("timer_"))
async def run_timer(call: types.CallbackQuery):
    await call.answer()
    
    # Разбиваем callback_data (например, timer_5_ex_push)
    parts = call.data.split("_")
    seconds = int(parts[1]) # Достаем время
    ex_type = f"{parts[2]}_{parts[3]}" # Восстанавливаем название (ex_push)
    
    chat_id = call.message.chat.id
    
    # Увеличиваем счетчик выполненных упражнений
    if chat_id not in user_stats:
         user_stats[chat_id] = {"ex_push": 0, "ex_squat": 0}
    
    if ex_type in user_stats[chat_id]:
        user_stats[chat_id][ex_type] += 1
    else:
        user_stats[chat_id][ex_type] = 1

    await call.message.edit_text(f"✅ Подход засчитан!\n⏳ Таймер отдыха запущен: {seconds} сек...")
    await asyncio.sleep(seconds)
    
    await call.message.edit_text("✅ Время вышло! Готов к следующему подходу?", reply_markup=get_exercises_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery):
    # Обнуляем статистику
    user_stats[call.message.chat.id] = {"ex_push": 0, "ex_squat": 0}
    await call.answer("Статистика успешно сброшена!", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
