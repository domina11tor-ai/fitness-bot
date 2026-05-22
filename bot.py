import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ВСТАВЬ СЮДА ТОКЕН СВОЕГО ВТОРОГО БОТА
TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню с кнопками тренировок и выбора отдыха
def get_main_keyboard():
    buttons = [
        [types.KeyboardButton(text="Пн (Силовая А)")],
        [types.KeyboardButton(text="Ср (Силовая Б)")],
        [types.KeyboardButton(text="Пт (Силовая В)")],
        [types.KeyboardButton(text="Отдых 30 сек"), types.KeyboardButton(text="Отдых 60 сек")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбери тренировку или время отдыха:", reply_markup=get_main_keyboard())

# Универсальная функция таймера
async def run_timer(message: types.Message, seconds: int):
    msg = await message.answer(f"Таймер отдыха: {seconds} сек")
    for i in range(seconds - 1, 0, -1):
        await asyncio.sleep(1)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Таймер отдыха: {i} сек")
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="Время вышло! Пора работать!")

@dp.message(F.text == "Отдых 30 сек")
async def timer_30(message: types.Message):
    await run_timer(message, 30)

@dp.message(F.text == "Отдых 60 сек")
async def timer_60(message: types.Message):
    await run_timer(message, 60)

# План тренировок
@dp.message(F.text == "Пн (Силовая А)")
async def day_a(message: types.Message):
    await message.answer("Понедельник (Силовая А):\n1. Отжимания: 4x15\n2. Приседания: 3x20")

@dp.message(F.text == "Ср (Силовая Б)")
async def day_b(message: types.Message):
    await message.answer("Среда (Силовая Б):\n1. Классика: 4x15\n2. Жим гантели: 3x12")

@dp.message(F.text == "Пт (Силовая В)")
async def day_c(message: types.Message):
    await message.answer("Пятница (Силовая В):\n1. Руки на возвышении: 4x15\n2. Выпады: 3x12")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
