import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand

TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_stats = {}

# --- КЛАВИАТУРЫ ---
def get_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 НАЧАТЬ ТРЕНИРОВКУ", callback_data="start_workout")
    kb.button(text="🔄 Сбросить статистику", callback_data="reset_stats")
    kb.button(text="Понедельник", callback_data="day_mon")
    kb.button(text="Среда", callback_data="day_wed")
    kb.button(text="Пятница", callback_data="day_fri")
    kb.adjust(1)
    return kb.as_markup()

def get_exercises_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="ex_push")
    kb.button(text="Приседания", callback_data="ex_squat")
    kb.button(text="🏁 ЗАВЕРШИТЬ ТРЕНИРОВКУ", callback_data="show_results")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

def get_rest_keyboard(exercise_code):
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 30 сек", callback_data=f"rest_30_{exercise_code}")
    kb.button(text="Отдых 40 сек", callback_data=f"rest_40_{exercise_code}")
    kb.button(text="⬅️ К упражнениям", callback_data="ex_menu")
    kb.adjust(2, 1)
    return kb.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери действие:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "reset_stats")
async def reset_stats(callback: types.CallbackQuery):
    user_stats[callback.message.chat.id] = {"ex_push": 0, "ex_squat": 0}
    await callback.answer("✅ Статистика сброшена!", show_alert=True)

@dp.callback_query(F.data == "start_workout")
async def start_workout(callback: types.CallbackQuery):
    user_stats[callback.message.chat.id] = {"ex_push": 0, "ex_squat": 0}
    await callback.message.edit_text("Тренировка начата! Выбери день:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "show_results")
async def show_results(callback: types.CallbackQuery):
    stats = user_stats.get(callback.message.chat.id, {"ex_push": 0, "ex_squat": 0})
    result_text = (f"🏆 Итоги тренировки:\n\n"
                   f"💪 Отжимания: {stats['ex_push']} подходов\n"
                   f"🦵 Приседания: {stats['ex_squat']} подходов\n\n"
                   f"Отличная работа! Нажми кнопку ниже для выхода.")
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В главное меню", callback_data="back_main")
    await callback.message.edit_text(result_text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.in_(["day_mon", "day_wed", "day_fri", "ex_menu"]))
async def show_exercises(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери упражнение:", reply_markup=get_exercises_keyboard())

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери день:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data.startswith("ex_"))
async def show_ex(callback: types.CallbackQuery):
    ex_code = callback.data.split("_")[1]
    text = "Отжимания (15 раз)" if ex_code == "push" else "Приседания (20 раз)"
    await callback.message.edit_text(f"{text}\nВыбери время отдыха:", reply_markup=get_rest_keyboard(ex_code))

@dp.callback_query(F.data.startswith("rest_"))
async def start_timer(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    seconds = int(parts[1])
    ex_code = parts[2]
    chat_id = callback.message.chat.id
    
    if chat_id not in user_stats: user_stats[chat_id] = {"ex_push": 0, "ex_squat": 0}
    user_stats[chat_id][f"ex_{ex_code}"] += 1
    current_count = user_stats[chat_id][f"ex_{ex_code}"]
    ex_name = "Отжиманий" if ex_code == "push" else "Приседаний"
    
    kb = InlineKeyboardBuilder()
    kb.button(text=f"✅ {ex_name}: {current_count} подходов", callback_data="none")
    
    msg = await callback.message.edit_text(f"Таймер: {seconds} сек", reply_markup=kb.as_markup())
    
    for i in range(seconds - 1, 0, -1):
        await asyncio.sleep(1)
        try: await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"Таймер: {i} сек", reply_markup=kb.as_markup())
        except: break
        
    await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, 
                               text=f"Время вышло! {ex_name} сделано: {current_count}.\nЧто делаем дальше?", 
                               reply_markup=get_exercises_keyboard())

async def main():
    await bot.set_my_commands([BotCommand(command="start", description="Запустить тренировку")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
