import asyncio
import os  # <--- ДОБАВЛЕНО ДЛЯ БЕЗОПАСНОСТИ
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ТЕПЕРЬ БЕЗОПАСНО: Бот берет токен из скрытых настроек Render, а не из кода!
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

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

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Выбери действие:", reply_markup=get_main_kb())

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

@dp.callback_query(F.data == "start_workout")
async def start_w(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="ex_push")
    kb.button(text="Приседания", callback_data="ex_squat")
    await call.message.edit_text("Выбери упражнение:", reply_markup=kb.as_markup())

# ВЫБОР ВРЕМЕНИ ОТДЫХА (ТАЙМЕР)
@dp.callback_query(F.data.startswith("ex_"))
async def select_ex(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 5 сек", callback_data="timer_5")
    kb.button(text="Отдых 10 сек", callback_data="timer_10")
    await call.message.edit_text("Выбери время отдыха:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("timer_"))
async def run_timer(call: types.CallbackQuery):
    await call.answer()
    seconds = int(call.data.split("_")[1])
    await call.message.edit_text(f"⏳ Таймер запущен: {seconds} сек...")
    await asyncio.sleep(seconds)
    await call.message.edit_text("✅ Время вышло! Готов к следующему подходу?", reply_markup=get_main_kb())

@dp.callback_query(F.data == "back_main")
async def back(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("Главное меню:", reply_markup=get_main_kb())

@dp.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery):
    await call.answer("Сброшено!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
