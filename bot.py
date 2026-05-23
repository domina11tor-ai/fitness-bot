import asyncio
import os
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Логирование
logging.basicConfig(level=logging.INFO)

# Получение переменных
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- КЛАВИАТУРА ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.button(text="💡 Мотивация", callback_data="get_motivation")
    kb.adjust(2)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Привет! Я твой фитнес-помощник. Используй /ask [вопрос], чтобы спросить совета у AI.", reply_markup=get_main_kb())

@dp.message(Command("ask"))
async def ask_ai(msg: types.Message):
    query = msg.text.replace("/ask", "").strip()
    if not query:
        await msg.answer("Напиши вопрос после команды, например: /ask как накачать бицепс?")
        return
    
    await msg.answer("⏳ Думаю...")
    try:
        response = model.generate_content(query)
        await msg.answer(response.text)
    except Exception as e:
        await msg.answer("Ошибка связи с AI. Проверь настройки ключа.")
        logging.error(e)

@dp.callback_query(F.data == "start_workout")
async def workout(call: types.CallbackQuery):
    await call.message.edit_text("🏋️ Выбери упражнение или спроси AI через /ask!", reply_markup=get_main_kb())

# --- ЗАПУСК ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
