import asyncio
import os
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Логирование
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ИИ
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Клавиатуры
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Вес", callback_data="weight_menu")
    kb.adjust(2)
    return kb.as_markup()

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Бот онлайн! Используй /ask для ИИ.", reply_markup=get_main_kb())

@dp.message(Command("ask"))
async def ask_ai(msg: types.Message):
    query = msg.text.replace("/ask", "").strip()
    if not query:
        await msg.answer("Напиши вопрос после /ask")
        return
    await msg.answer("⏳ Думаю...")
    try:
        response = model.generate_content(query)
        await msg.answer(response.text)
    except Exception as e:
        await msg.answer(f"Ошибка ИИ: {e}")

@dp.callback_query(F.data == "start_workout")
async def workout(call: types.CallbackQuery):
    await call.answer("Загрузка...")
    await call.message.answer("🏋️ Раздел тренировок открыт!")

async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(status=200)

async def main():
    # Удаляем вебхук, чтобы "обнулить" состояние
    await bot.delete_webhook(drop_pending_updates=True)
    
    app = web.Application()
    app.router.add_post(f'/{TOKEN}', handle_webhook)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    # Установка нового вебхука
    await bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    print(f"Webhook установлен на {WEBHOOK_URL}/{TOKEN}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
