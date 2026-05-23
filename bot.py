# ... (оставляем импорты и инициализацию как есть) ...

# 1. Добавляем список упражнений
WORKOUTS = {
    "push": "💪 Отжимания (3 подхода по 15 раз)",
    "squat": "🦵 Приседания (4 подхода по 20 раз)",
    "press": "🔥 Пресс (3 подхода по 30 секунд)"
}

# 2. Обновленное меню тренировок
def get_workout_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отжимания", callback_data="w_push")
    kb.button(text="Приседания", callback_data="w_squat")
    kb.button(text="Пресс", callback_data="w_press")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

# 3. Обработчик нажатия на "Тренировка" (показывает список)
@dp.callback_query(F.data == "start_workout")
async def workout_list(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("🏋️ Выбери упражнение:", reply_markup=get_workout_kb())

# 4. Обработчик конкретного упражнения
@dp.callback_query(F.data.startswith("w_"))
async def show_exercise(call: types.CallbackQuery):
    workout_key = call.data.split("_")[1]
    text = WORKOUTS.get(workout_key, "Упражнение не найдено")
    await call.answer()
    await call.message.edit_text(f"{text}\n\nЧто дальше?", reply_markup=get_workout_kb())

# 5. Кнопка "Назад"
@dp.callback_query(F.data == "back_main")
async def back_to_main(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text("🔥 Fitness Pro готов!", reply_markup=get_main_kb())

# ... (остальной код main и webhook остается без изменений) ...
