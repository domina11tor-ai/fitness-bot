import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Храним счетчики подходов: {chat_id: count}
user_sets = {}

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
    # При нажатии на отдых - подход засчитывается автоматически
    kb.button(text="Отдых 30 сек", callback_data="rest_30")
    kb.button(text="Отдых 40 сек", callback_data="rest_40")
    kb.button(text="⬅️ Назад к упражнениям", callback_data="ex_menu")
    kb.adjust(2, 1)
    return kb.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_sets[message.chat.id] = 0
    await message.answer("Привет! Выбери день:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data.in_(["day_mon", "day_wed", "day_fri", "ex_menu"]))
async def show_exercises(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери упражнение:", reply_markup=get_exercises_keyboard())

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выбери день:", reply_markup=get_main_keyboard())

@dp.callback_query(F.data.startswith("ex_"))
async def show_ex(callback: types.CallbackQuery):
    text = "Отжимания (15 раз)" if callback.data == "ex_push" else "Приседания (20 раз)"
    await callback.message.edit_text(f"{text}\nВыбери время отдыха (подход засчитается автоматически):", 
                                     reply_markup=get_rest_keyboard())

@dp.callback_query(F.data.startswith("rest_"))
async def start_timer(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    # 1. Автоматически засчитываем подход
    user_sets[chat_id] = user_sets.get(chat_id, 0) + 1
    
    seconds = int(callback.data.split("_")[1])
    
    # 2. Показываем сообщение с новым счетчиком и таймером
    msg = await callback.message.edit_text(f"✅ Подход №{user_sets[chat_id]} засчитан!\n\nТаймер отдыха: {seconds} сек")
    
    for i in range(seconds - 1, 0, -1):
        await asyncio.sleep(1)
        try: 
            await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, 
                                      text=f"✅ Подход №{user_sets[chat_id]} засчитан!\n\nТаймер отдыха: {i} сек")
        except: break
        
    await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, 
                               text=f"Время вышло! Подход №{user_sets[chat_id]} завершен.\nЧто делаем дальше?", 
                               reply_markup=get_exercises_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
