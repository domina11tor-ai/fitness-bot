import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand

# ЗАМЕНИ НА НОВЫЙ ТОКЕН ИЗ BOTFATHER!
TOKEN = "8695430253:AAF1IR-ZYmrQ0PcdSgNxVD8yGxEhd-Jk3bA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_stats = {}

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 НАЧАТЬ ТРЕНИРОВКУ", callback_data="start_workout")
    kb.button(text="🔄 Сбросить", callback_data="reset")
    kb.button(text="Понедельник", callback_data="day_mon")
    kb.button(text="Среда", callback_data="day_wed")
    kb.button(text="Пятница", callback_data="day_fri")
    kb.adjust(1)
    return kb.as_markup()

def get_ex_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="ex_push")
    kb.button(text="Приседания", callback_data="ex_squat")
    kb.button(text="🏁 ЗАВЕРШИТЬ", callback_data="show_results")
    kb.button(text="⬅️ Меню", callback_data="back_main")
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
    user_stats[call.message.chat.id] = {"ex_push": 0, "ex_squat": 0}
    await call.message.edit_text("Тренировка начата! Выбери упражнение:", reply_markup=get_ex_kb())

@dp.callback_query(F.data.startswith("ex_"))
async def select_ex(call: types.CallbackQuery):
    await call.answer()
    ex = call.data.split("_")[1]
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 30с", callback_data=f"rest_30_{ex}")
    kb.button(text="Отдых 40с", callback_data=f"rest_40_{ex}")
    await call.message.edit_text("Выбери отдых:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("rest_"))
async def timer(call: types.CallbackQuery):
    await call.answer()
    _, sec, ex = call.data.split("_")
    chat_id = call.message.chat.id
    user_stats.setdefault(chat_id, {"ex_push": 0, "ex_squat": 0})[f"ex_{ex}"] += 1
    
    await call.message.edit_text(f"✅ Подход засчитан! Таймер: {sec}с...")
    await asyncio.sleep(int(sec))
    await call.message.edit_text("Время вышло! Выбери следующее:", reply_markup=get_ex_kb())

@dp.callback_query(F.data == "show_results")
async def results(call: types.CallbackQuery):
    await call.answer()
    stats = user_stats.get(call.message.chat.id, {"ex_push": 0, "ex_squat": 0})
    await call.message.edit_text(f"🏆 Итоги:\nОтжимания: {stats['ex_push']}\nПриседания: {stats['ex_squat']}", 
                                 reply_markup=get_main_kb())

@dp.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery):
    await call.answer("Сброшено!", show_alert=True)
    user_stats[call.message.chat.id] = {"ex_push": 0, "ex_squat": 0}

async def main():
    await bot.set_my_commands([BotCommand(command="start", description="Старт")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
