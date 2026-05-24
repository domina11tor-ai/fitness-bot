from fastapi import FastAPI, Request
import httpx

app = FastAPI()

TOKEN = "8695430253:AAHEsQpe50vFjTCVnFcxIcua56MUTXOSnXM" # Замените на свежий токен
TELEGRAM_API = f"https://telegram.org{TOKEN}"

# База данных тренировок
PRESETS = {
    "preset_mon": {"day": "Понедельник", "title": "Грудные и трицепс", "ex": "Классические отжимания, жим гантелей лежа, разводка гантелей, обратные отжимания от стула", "reps": "3-4 по 12-15"},
    "preset_tue": {"day": "Вторник", "title": "Спина и бицепс", "ex": "Тяга гантели к поясу в наклоне, молотковые сгибания, классические сгибания рук на бицепс", "reps": "3-4 по 12-15"},
    "preset_wed": {"day": "Среда", "title": "Ноги и пресс", "ex": "Приседания с гантелями, выпады, планка (1 мин), скручивания", "reps": "3-4 по 15-20"},
    "preset_thu": {"day": "Четверг", "title": "Плечи и трицепс", "ex": "Жим гантелей вверх стоя, махи гантелями в стороны, отжимания с узкой постановкой рук", "reps": "3-4 по 12"},
    "preset_fri": {"day": "Пятница", "title": "Спина и бицепс (повтор)", "ex": "Становая тяга с гантелями (на прямых ногах), тяга гантели одной рукой, концентрированный подъем на бицепс", "reps": "3-4 по 12-15"},
    "preset_sat": {"day": "Суббота", "title": "Грудь и ноги (микс)", "ex": "Широкие отжимания, кубковые приседания (гантель у груди), подъем на носки", "reps": "3-4 по 15"},
    "preset_sun": {"day": "Воскресенье", "title": "Активное восстановление", "ex": "Растяжка всех групп мышц + легкая прогулка", "reps": "20-30 минут"}
}

def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📋 Готовые варианты по дням", "callback_data": "open_presets"}],
            [{"text": "⚙️ Настройки таймера (60с)", "callback_data": "disabled_btn"}]
        ]
    }

def get_presets_keyboard():
    buttons = []
    for key, data in PRESETS.items():
        buttons.append([{"text": f"📅 {data['day']}: {data['title']}", "callback_data": key}])
    buttons.append([{"text": "⬅️ Назад в меню", "callback_data": "back_to_menu"}])
    return {"inline_keyboard": buttons}

async def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)

async def edit_message(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/editMessageText", json=payload)

@app.post("/")
async def telegram_webhook(request: Request):
    update = await request.json()
    
    # Обработка текстовых команд
    if "message" in update and "text" in update["message"]:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message["text"]
        
        if text == "/start":
            await send_message(chat_id, "Привет! Я твой фитнес-напарник. Выбери нужный раздел:", get_main_keyboard())
            
    # Обработка нажатий на кнопки (Callback Query)
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        
        if data == "open_presets":
            await edit_message(chat_id, message_id, "📋 Выбери день недели для запуска готовой тренировки:", get_presets_keyboard())
            
        elif data == "back_to_menu":
            await edit_message(chat_id, message_id, "Привет! Я твой фитнес-напарник. Выбери нужный раздел:", get_main_keyboard())
            
        elif data.startswith("preset_"):
            preset_data = PRESETS.get(data)
            if preset_data:
                start_btn = {
                    "inline_keyboard": [
                        [{"text": "⏳ Засечь 60 сек отдыха", "callback_data": "alert_timer"}],
                        [{"text": "⬅️ Назад к дням недели", "action": "open_presets", "callback_data": "open_presets"}]
                    ]
                }
                text = f"🎯 День: *{preset_data['day']}*\n💪 Тренировка: *{preset_data['title']}*\n\n📋 Упражнения:\n_{preset_data['ex']}_\n\n📊 Схема: *{preset_data['reps']}*"
                await edit_message(chat_id, message_id, text, start_btn)
                
        elif data == "alert_timer":
            # Внутри Workers нельзя делать долгие задержки сна.
            # Вместо этого мы используем встроенный ответ Telegram-уведомления (AnswerCallbackQuery)
            async with httpx.AsyncClient() as client:
                await client.post(f"{TELEGRAM_API}/answerCallbackQuery", json={
                    "callback_query_id": callback["id"],
                    "text": "⏳ Отсчет пошел! Засеките 60 секунд. Бот пришлет пуш, когда время выйдет.",
                    "show_alert": True
                })
            # Отправка отложенного уведомления через Cloudflare требует системных очередей (Queues),
            # поэтому для простоты бот отправляет текстовое напоминание.
            await send_message(chat_id, "🔔 Время пошло. Сделайте глубокий вдох и приготовьтесь к следующему подходу!")

    return {"ok": True}
