import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web 

TOKEN = os.getenv("BOT_TOKEN") 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище статистики пользователей
user_stats = {}

DAY_NAMES = {
    "day_mon": "Понедельник",
    "day_tue": "Вторник",
    "day_wed": "Среда",
    "day_thu": "Четверг",
    "day_fri": "Пятница",
    "day_sat": "Суббота",
    "day_sun": "Воскресенье"
}

# ПОЛНАЯ ПРОГРАММА НА 7 ДНЕЙ С БОЛГАРСКИМИ ПРИСЕДАНИЯМИ
EXERCISES_BY_DAY = {
    "day_mon": {"push": "Отжимания 4х15-20", "press_db": "Жим гантелей лежа 4х15-20", "narrow": "Узкие отжимания 4х15-20"},
    "day_tue": {"row_db": "Тяга гантели к поясу 4х15-20", "hammer": "Молотковые сгибания 4х15-20", "biceps": "Классический бицепс 4х15-20"},
    "day_wed": {"squat": "Приседания с гантелями 4х20", "bulgarian": "Болгарские приседания 4х20", "plank": "Планка 4х1 мин"},
    "day_thu": {"press_up": "Жим гантелей вверх 4х12-15", "lateral": "Махи в стороны 4х12-15", "dips": "Обратные отжимания 4х12-15"},
    "day_fri": {"deadlift": "Становая тяга 4х15-20", "row_one": "Тяга 1 рукой 4х15-20", "biceps_conc": "Концентрированный бицепс 4х15-20"},
    "day_sat": {"wide_push": "Широкие отжимания 4х20", "goblet": "Кубковые приседания 4х20", "calf": "Подъем на носки 4х20"},
    "day_sun": {"rest": "Растяжка всего тела + легкая прогулка (День отдыха)"}
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
    kb.button(text="ПН (Грудь/Трицепс)", callback_data="workout_day_mon")
    kb.button(text="ВТ (Спина/Бицепс)", callback_data="workout_day_tue")
    kb.button(text="СР (Ноги/Пресс)", callback_data="workout_day_wed")
    kb.button(text="ЧТ (Плечи/Трицепс)", callback_data="workout_day_thu")
    kb.button(text="ПТ (Спина/Бицепс)", callback_data="workout_day_fri")
    kb.button(text="СБ (Грудь/Ноги)", callback_data="workout_day_sat")
    kb.button(text="ВС (Восстановление)", callback_data="workout_day_sun")
    kb.button(text="⬅️ Главное меню", callback_data="back_main")
    kb.adjust(2, 2, 2, 1, 1) # Красивое распределение кнопок по парам
    return kb.as_markup()

def get_exercises_kb(day_key, chat_id):
    kb = InlineKeyboardBuilder()
    exercises = EXERCISES_BY_DAY.get(day_key, {})
    day_stats = user_stats.get(chat_id, {}).get(day_key, {})
    
    for ex_id, ex_name in exercises.items():
        count = day_stats.get(f"ex_{ex_id}", 0)
        # Динамический счетчик выполненных упражнений (+1 подх.)
        btn_text = f"{ex_name} ✅ {count}" if count > 0 else ex_name
        kb.button(text=btn_text, callback_data=f"run_ex_{ex_id}_{day_key}")
        
    kb.button(text="🏁 Завершить тренировку", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()


# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Добро пожаловать в твой тренировочный дневник 💪\nВыбери действие:", reply_markup=get_main_kb())

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
        "day_mon": "📅 План на ПОНЕДЕЛЬНИК (Грудь и трицепс):\n- Отжимания: 4х15-20\n- Жим гантелей лежа: 4х15-20\n- Узкие отжимания: 4х15-20",
        "day_tue": "📅 План на ВТОРНИК (Спина и бицепс):\n- Тяга гантели к поясу: 4х15-20\n- Молотковые сгибания: 4х15-20\n- Классический бицепс: 4х15-20",
        "day_wed": "📅 План на СРЕДУ (Ноги и пресс):\n- Приседания с гантелями: 4х20\n- Болгарские приседания: 4х20\n- Планка: 4х1 мин",
        "day_thu": "📅 План на ЧЕТВЕРГ (Плечи и трицепс):\n- Жим гантелей вверх: 4х12-15\n- Махи в стороны: 4х12-15\n- Обратные отжимания от стула: 4х12-15",
        "day_fri": "📅 План на ПЯТНИЦУ (Спина и бицепс):\n- Становая тяга (на прямых ногах): 4х15-20\n- Тяга 1 рукой: 4х15-20\n- Концентрированный бицепс: 4х15-20",
        "day_sat": "📅 План на СУББОТУ (Грудь и ноги):\n- Широкие отжимания: 4х20\n- Кубковые приседания: 4х20\n- Подъем на носки (икры): 4х20",
        "day_sun": "📅 План на ВОСКРЕСЕНЬЕ:\n- Восстановление: Растяжка всего тела + легкая прогулка (30-45 мин)"
    }
    
    text = plans.get(day_key, "План не найден.")
    
    kb = InlineKeyboardBuilder()
    if day_key != "day_sun":
        kb.button(text="🏋️ Начать упражнения", callback_data=f"start_ex_{day_key}")
    kb.button(text="⬅️ Назад к дням", callback_data="start_workout")
    kb.adjust(1)
    
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("start_ex_"))
async def start_exercises(call: types.CallbackQuery):
    await call.answer()
    day_key = call.data.replace("start_ex_", "")
    chat_id = call.message.chat.id
    
    await call.message.edit_text(
        f"🏃 Тренировка идет. День: {DAY_NAMES.get(day_key)}.\nВыбери упражнение:", 
        reply_markup=get_exercises_kb(day_key, chat_id)
    )

@dp.callback_query(F.data.startswith("run_ex_"))
async def select_timer(call: types.CallbackQuery):
    await call.answer()
    parts = call.data.replace("run_ex_", "").split("_")
    ex_id = parts[0] 
    day_key = f"{parts[1]}_{parts[2]}" 
    
    kb = InlineKeyboardBuilder()
    # ТАЙМЕРЫ ИЗМЕНЕНЫ НА 30 И 40 СЕКУНД ПО ЗАПРОСУ Пользователя
    kb.button(text="⏱ Отдых 30 сек", callback_data=f"t_30_{ex_id}_{day_key}") 
    kb.button(text="⏱ Отдых 40 сек", callback_data=f"t_40_{ex_id}_{day_key}") 
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
    
    # Засчитываем выполненный подход
    if chat_id not in user_stats:
        user_stats[chat_id] = {}
    if day_key not in user_stats[chat_id]:
        user_stats[chat_id][day_key] = {}
        
    ex_key = f"ex_{ex_id}"
    if ex_key not in user_stats[chat_id][day_key]:
        user_stats[chat_id][day_key][ex_key] = 0
        
    user_stats[chat_id][day_key][ex_key] += 1
    current_sets = user_stats[chat_id][day_key][ex_key]
    ex_name = EXERCISES_BY_DAY[day_key][ex_id].split(" ")[0] # Вычленяем имя упражнения

    # Живой таймер обратного отсчета с шагом в 5 секунд
    step = 5
    for remaining in range(seconds, 0, -step):
        try:
            await call.message.edit_text(
                f"✅ {ex_name} (+1 подх.)\nВсего выполнено: {current_sets}\n\n⏳ Осталось отдыхать: {remaining} сек..."
            )
        except:
            pass
        await asyncio.sleep(step)
    
    # Возвращаем пользователя к списку упражнений дня
    await call.message.edit_text(
        f"💪 Время отдыха вышло! Продолжаем тренировку за {DAY_NAMES.get(day_key)}.\nВыбери упражнение:", 
        reply_markup=get_exercises_kb(day_key, chat_id)
    )

@dp.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery):
    await call.answer()
    chat_id = call.message.chat.id
    stats = user_stats.get(chat_id, {})
    
    text = "📊 **Твоя полная статистика по подходам:**\n\n"
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
    await call.answer("Вся статистика тренировок очищена!", show_alert=True)
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())


# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ РАБОТЫ НА RENDER ---
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000)) 
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await asyncio.gather(
        start_dummy_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
