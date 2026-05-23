import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web # <--- Новая библиотека для сервера-заглушки

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

@dp.callback_query(F.data == "start_workout")
async def start_w(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выбери день недели для тренировки:", reply_markup=get_days_kb())

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

@dp.callback_query(F.data.startswith("start_ex_"))
async def start_exercises(call: types.CallbackQuery):
    await call.answer()
    day_key = call.data.replace("start_ex_", "")
    
    await call.message.edit_text(
        f"🏃 Тренировка идет. День: {DAY_NAMES.get(day_key)}.\nВыбери упражнение:", 
        reply_markup=get_exercises_kb(day_key)
    )

@dp.callback_query(F.data.startswith("run_ex_"))
async def select_timer(call: types.CallbackQuery):
    await call.answer()
    parts = call.data.replace("run_ex_", "").split("_")
    ex_id = parts[0] 
    day_key = f"{parts[1]}_{parts[2]}" 
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 20 сек", callback_data=f"t_20_{ex_id}_{day_key}") 
    kb.button(text="Отдых 30 сек", callback_data=f"t_30_{ex_id}_{day_key}") 
    kb.button(text="⬅️ Назад к упражнениям", callback_data=f"start_ex_{day_key}")
    kb.adjust(1)
    
    await call.message.edit_text("Подход выполнен! Сколько будем отдыхать?", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("t_"))
async def run_timer(call: types.CallbackQuery):
    await call.answer()
    
    parts = call.data.split("_")
    seconds = int(parts[1])
    ex_id = parts[2] 
    day_key = f"{parts[3]}_{parts[4]}" 
    
    chat_id = call.message.chat.id
    
    if chat_id not in user_stats:
        user_stats[chat_id] = {}
    if day_key not in user_stats[chat_id]:
        user_stats[chat_id][day_key] = {}
        
    ex_key = f"ex_{ex_id}"
    if ex_key not in user_stats[chat_id][day_key]:
        user_stats[chat_id][day_key][ex_key] = 0
        
    user_stats[chat_id][day_key][ex_key] += 1

    await call.message.edit_text(f"✅ Подход засчитан!\n⏳ Отдых: {seconds} сек...")
    await asyncio.sleep(seconds)
    
    await call.message.edit_text(
        f"💪 Время вышло! Продолжаем тренировку за {DAY_NAMES.get(day_key)}.\nВыбери упражнение:", 
        reply_markup=get_exercises_kb(day_key)
    )

@dp.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery):
    await call.answer()
    chat_id = call.message.chat.id
    stats = user_stats.get(chat_id, {})
    
    text = "📊 **Твоя статистика по дням недели:**\n\n"
    for day_key, day_name in DAY_NAMES.items():
        text += f"🔹 **{day_name}:**\n"
        day_data = stats.get(day_key, {})
        
        for ex_id, ex_name in EXERCISES_BY_DAY[day_key].items():
            count = day_data.get(f"ex_{ex_id}", 0)
            text += f"   - {ex_name}: {count} подх.\n"
        text += "\n"
        
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад в меню", callback_data="back_main")
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery):
    user_stats[call.message.chat.id] = {}
    await call.answer("Вся статистика очищена!", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())


# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передает свой порт в переменную PORT
    port = int(os.environ.get("PORT", 10000)) 
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    # Одновременно запускаем и сервер-заглушку, и самого бота
    await asyncio.gather(
        start_dummy_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
