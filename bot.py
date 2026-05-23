import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура главного меню
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.adjust(2)
    return kb.as_markup()

# Обработка команды /start
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Бот готов! Выбери действие:", reply_markup=get_main_kb())

# Обработка кнопки "Тренировка"
@dp.callback_query(F.data == "start_workout")
async def workout_handler(call: types.CallbackQuery):
    # ОБЯЗАТЕЛЬНО отвечаем на callback, чтобы убрать "часики" с кнопки
    await call.answer()
    await call.message.edit_text("🏋️ Раздел тренировок!", reply_markup=get_main_kb())

# --- ЗАПУСК БОТА ---
async def main():
    # Удаляем вебхук при старте, чтобы Polling заработал без ошибок
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен в режиме Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
