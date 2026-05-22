import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ВСТАВЬ СЮДА ТОКЕН СВОЕГО ВТОРОГО БОТА
TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню с кнопками тренировок
def get_main_keyboard():
    buttons = [
        [types.KeyboardButton(text="Пн (Силовая А)")],
        [types.KeyboardButton(text="Ср (Силовая Б)")],
        [types.KeyboardButton(text="Пт (Силовая В)")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой фитнес-бот. Выбери день недели, чтобы посмотреть план тренировки:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "Пн (Силовая А)")
async def day_a(message: types.Message):
    text = (
        "Понедельник (Силовая А):\n\n"
        "1. Отжимания (широкий хват): 3-4 подхода по 12-15 раз\n"
        "2. Отжимания (узкий хват): 3 подхода по 8-10 раз\n"
        "3. Приседания: 3 подхода по 15-20 раз"
    )
    await message.answer(text)

@dp.message(F.text == "Ср (Силовая Б)")
async def day_b(message: types.Message):
    text = (
        "Среда (Силовая Б):\n\n"
        "1. Отжимания от пола (классика): 4 подхода по 12-15 раз\n"
        "2. Махи гантелью перед собой (5 кг): 3 подхода по 12 раз\n"
        "3. Жим гантели стоя (5 кг): 3 подхода по 10-12 раз"
    )
    await message.answer(text)

@dp.message(F.text == "Пт (Силовая В)")
async def day_c(message: types.Message):
    text = (
        "Пятница (Силовая В):\n\n"
        "1. Отжимания (руки на возвышении): 3-4 подхода по 15 раз\n"
        "2. Махи гантелью в стороны (5 кг): 3 подхода по 12 раз\n"
        "3. Выпады: 3 подхода по 12 раз на каждую ногу"
    )
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
