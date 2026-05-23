import asyncio
import os
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)

# 2. Инициализация Bot и Dispatcher (это должно быть в начале!)
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 3. Настройка ИИ
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- КЛАВИАТУРЫ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="menu_workout")
    kb.button(text="⚖️ Вес", callback_data="menu_weight")
    kb.adjust(2)
    return kb.as_markup()

def get_workout_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 План на неделю", callback_data="show_plan")
    kb.button(text="⬅️ Назад", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 Fitness Pro запущен!", reply_markup=get_main_kb())

@dp.message(Command("ask"))
async def ask_ai(msg: types.Message):
    query = msg.text.replace("/ask", "").strip()
    if not query:
        await msg.answer("Напиши вопрос, например: /ask как качать пресс?")
        return
    await msg.answer("⏳ Думаю...")
    try:
        response = model.generate_content(query)
        await msg.answer(response.text)
    except Exception as e:
        await msg.answer(f"Ошибка ИИ: {e}")

# --- НАВИГАЦИЯ ---
@dp.callback_query(F.data.startswith("menu_"))
async def main_navigation(call: types.CallbackQuery):
    await call.answer()
    if call.data == "menu_workout":
        await call.message.edit_text("🏋️ Раздел тренировок. Что выберешь?", reply_markup=get_workout_kb())
    elif call.data == "menu_weight":
        await call.message.edit_text("⚖️ Твой текущий вес: 80кг", reply_markup=get_workout_kb())

@dp.callback_query(F.data == "show_plan")
async def show_plan(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("📅 План на 7 дней:\nПн-Ср: Кардио\nЧт-Сб: Силовые\nВс: Отдых", reply_markup=get_workout_kb())

@dp.callback_query(F.data == "main_menu")
async def back_to_main(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("🔥 Fitness Pro готов!", reply_markup=get_main_kb())

# --- WEBHOOK ЛОГИКА ---
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(status=200)

async def main():
    app = web.Application()
    app.router.add_post(f'/{TOKEN}', handle_webhook)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    # Сбрасываем старый вебхук и ставим новый
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    logging.info(f"Webhook set to {WEBHOOK_URL}/{TOKEN}")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
