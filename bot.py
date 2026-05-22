import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ВСТАВЬ СЮДА ТОКЕН СВОЕГО ВТОРОГО БОТА
TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МЕНЮ ---
def get_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Понедельник", callback_data="day_mon")
    kb.button(text="Среда", callback_data="day_wed")
    kb.button(text="Пятница", callback_data="day_fri")
    kb.adjust(1)
    return kb.as_markup()

def get_exercises_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="ex_push")
    kb.button(text="Приседания", callback_data="ex_squat")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

def get_rest_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отдых 30 сек", callback_data="rest_30")
    kb.button(text="Отдых 40 сек", callback_data="rest_40")
    return kb.as_markup()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери день тренировки:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data.startswith("day_"))
async def day_chosen(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери упражнение:", reply_markup=get_exercises_keyboard())

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери день тренировки:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "ex_push")
async def show_push(callback: types.CallbackQuery):
    await callback.message.edit_text("Отжимания: 3-4 подхода по 15 повторений.\nВыбери отдых:", reply_markup=get_rest_keyboard())

@dp.callback_query(F.data == "ex_squat")
async def show_squat(callback: types.CallbackQuery):
    await callback.message.edit_text("Приседания: 3-4 подхода по 20 повторений.\nВыбери отдых:", reply_markup=get_rest_keyboard())

@dp.callback_query(F.data.startswith("rest_"))
async def start_timer(callback: types.CallbackQuery):
    seconds = int(callback.data.split("_")[1])
    msg = await callback.message.edit_text(f"Таймер: {seconds} сек")
    for i in range(seconds - 1, 0, -1):
        await asyncio.sleep(1)
        try:
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=msg.message_id, text=f"Таймер: {i} сек")
        except: break
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=msg.message_id, text="Время вышло! Вперед!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
