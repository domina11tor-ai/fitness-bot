# --- НОВАЯ ЛОГИКА ДЛЯ ВЕСА ---
@dp.callback_query(F.data == "weight_menu")
async def weight_menu(call: types.CallbackQuery):
    await call.message.edit_text("Введи свой вес в сообщении (просто число, например: 85):")
    # Чтобы бот понял следующее сообщение как вес, нам нужно добавить состояние, 
    # но пока для простоты можно использовать команду /weight 85

@dp.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def save_weight(msg: types.Message):
    weight = float(msg.text)
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET weight = ? WHERE user_id = ?", (weight, msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer(f"Вес {weight} кг успешно сохранен!", reply_markup=get_main_kb())

# --- ЛОГИКА ДЛЯ ТРЕНИРОВКИ ---
@dp.callback_query(F.data == "start_workout")
async def start_workout(call: types.CallbackQuery):
    # Увеличиваем XP за открытие меню тренировки
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + 10 WHERE user_id = ?", (call.from_user.id,))
    conn.commit()
    conn.close()
    await call.message.edit_text("🏋️ Время тренироваться! Выбери упражнение (скоро добавим список):", reply_markup=get_main_kb())
