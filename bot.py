import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from google import genai

# 1. Логирование
logging.basicConfig(level=logging.INFO)

# 2. Переменные
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = genai.Client(api_key=GEMINI_KEY)

# 3. Меню
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="menu_workout")
    kb.button(text="⚖️ Вес", callback_data="menu_weight")
    kb.adjust(2)
    return kb.as_markup()

# 4. Обработчики
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Fitness Pro готов!", reply_markup=get_main_kb())

@dp.callback_query(F.data.startswith("menu_"))
async def main_nav(call: types.CallbackQuery):
    await call.answer()
    if call.data == "menu_workout":
        await call.message.edit_text("🏋️ Раздел тренировок: [Список упражнений]", reply_markup=get_main_kb())
    elif call.data == "menu_weight":
        await call.message.edit_text("⚖️ Вес: 80 кг", reply_markup=get_main_kb())

# 5. Веб-сервер
async def handle_webhook(request):
    data = await request.json()
    await dp.feed_update(bot, types.Update(**data))
    return web.Response(status=200)

async def main():
    app = web.Application()
    app.router.add_post(f'/{TOKEN}', handle_webhook)
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # ПРИНУДИТЕЛЬНАЯ УСТАНОВКА
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(webhook_url)
    logging.info(f"Сервер запущен. Вебхук установлен на: {webhook_url}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
