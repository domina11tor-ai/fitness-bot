import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web

# Логирование
logging.basicConfig(level=logging.INFO)

# Переменные из Render
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://твое-имя.onrender.com

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Бот запущен через Webhook и готов к работе.")

async def handle_webhook(request):
    """Обработчик входящих обновлений от Telegram"""
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(status=200)

async def main():
    app = web.Application()
    # Роут будет выглядеть как /<TOKEN>
    app.router.add_post(f'/{TOKEN}', handle_webhook)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт для Render
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # Установка вебхука
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook set to {webhook_url}")
    
    # Вечное ожидание
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
