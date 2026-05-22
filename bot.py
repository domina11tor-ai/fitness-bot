import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Сюда вставляешь токен от @BotFather (внутри кавычек)
TOKEN = "8695430253:AAGjaf_a9UwV0tS_v53sIx6t41I93GNE5cw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Твой план тренировок
WORKOUT_PLAN = {
    "monday": {
        "title": "Понедельник (Силовая А)",
        "exercises": "• Отжимания: 4 подходов х 12-15 повторений\n• Приседания: 4 подходов х 20 повторений\n• Махи с гантелью: 4 подходов х 15 повторений"
    },
    "wednesday": {
        "title": "Среда (Силовая Б)",
        "exercises": "• Отжимания (широкий хват): 4 подходов х 12 повторений\n• Выпады: 4 подходов х 12 повторений на ногу\n• Подъем гантели на бицепс: 4 подходов х 15 повторений"
    },
    "friday": {
        "title": "Пятница (Фулбоди)",
        "exercises": "• Отжимания: 4 подходов х 15 повторений\n• Алмазные отжимания: 3 подходов х 10 повторений\n• Приседания + жим гантели: 4 подходов х 12 повторений"
    }
}

def get_days_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Понедельник", callback_data="day_monday")],
        [InlineKeyboardButton(text="Среда", callback_data="day_wednesday")],
        [InlineKeyboardButton(text="Пятница", callback_data="day_friday")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_workout_keyboard(day: str):
    buttons = [
        [InlineKeyboardButton(text="⏱️ Запустить отдых (2 мин)", callback_data=f"timer_120_{day}")],
        [InlineKeyboardButton(text="🔙 Назад к дням", callback_data="back_to_days")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Выбери день недели, чтобы посмотреть план тренировки:",
        reply_markup=get_days_keyboard()
    )

@dp.callback_query(F.data.startswith("day_"))
async def show_workout(callback: CallbackQuery):
    day = callback.data.split("_")[1]
    workout = WORKOUT_PLAN.get(day)
    
    if workout:
        text = f"🏋️‍♂️ **{workout['title']}**\n\n{workout['exercises']}"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_workout_keyboard(day))
    else:
        await callback.message.edit_text("На этот день план пуст!", reply_markup=get_days_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_days")
async def back_to_days(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери день недели, чтобы посмотреть план тренировки:",
        reply_markup=get_days_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("timer_"))
async def start_timer(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    seconds = int(data_parts[1])
    day = data_parts[2]
    
    workout = WORKOUT_PLAN.get(day)
    base_text = f"🏋️‍♂️ **{workout['title']}**\n\n{workout['exercises']}\n\n"

    await callback.answer("Таймер запущен!", show_alert=False)

    for left in range(seconds, 0, -10):
        minutes_left = left // 60
        seconds_left = left % 60
        timer_text = f"⏳ **Отдых: {minutes_left:02d}:{seconds_left:02d}**"
        
        try:
            await callback.message.edit_text(
                base_text + timer_text,
                parse_mode="Markdown",
                reply_markup=get_workout_keyboard(day)
            )
        except Exception:
            return
        await asyncio.sleep(10)

    try:
        await callback.message.edit_text(
            base_text + "🔔 **Время отдыха вышло! Делаем следующий подход!**",
            parse_mode="Markdown",
            reply_markup=get_workout_keyboard(day)
        )
    except Exception:
        pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
      
