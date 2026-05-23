import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
# URL, который выдаст тебе Render после деплоя (например, https://my-bot.onrender.com)
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Бот запущен через Webhook!")

async def on_startup():
    # Устанавливаем вебхук при старте
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

async def handle_webhook(request):
    # Обработка обновлений от Telegram
    url = str(request.url)
    index = url.rfind('/')
    token = url[index + 1:]
    if token != TOKEN:
        return web.Response(status=403)
    
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

async def main():
    app = web.Application()
    app.router.add_post(f'/webhook', handle_webhook)
    
    # Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    await on_startup()
    await asyncio.Event().wait() # Держим процесс открытым

if __name__ == "__main__":
    asyncio.run(main())
