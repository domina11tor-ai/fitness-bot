import json
import urllib.request

# Ваша тренировочная программа на всю неделю из ваших таблиц
PRESETS = {
    "preset_mon": {
        "day": "Понедельник",
        "title": "Грудные и трицепс",
        "ex": "Классические отжимания, жим гантелей лежа, разводка гантелей, обратные отжимания от стула",
        "reps": "3-4 по 12-15"
    },
    "preset_tue": {
        "day": "Вторник",
        "title": "Спина и бицепс",
        "ex": "Тяга гантели к поясу в наклоне, молотковые сгибания, классические сгибания рук на бицепс",
        "reps": "3-4 по 12-15"
    },
    "preset_wed": {
        "day": "Среда",
        "title": "Ноги и пресс",
        "ex": "Приседания с гантелями, выпады, планка (1 мин), скручивания",
        "reps": "3-4 по 15-20"
    },
    "preset_thu": {
        "day": "Четверг",
        "title": "Плечи и трицепс",
        "ex": "Жим гантелей вверх стоя, махи гантелями в стороны, отжимания с узкой постановкой рук",
        "reps": "3-4 по 12"
    },
    "preset_fri": {
        "day": "Пятница",
        "title": "Спина и бицепс (повтор)",
        "ex": "Становая тяга с гантелями (на прямых ногах), тяга гантели одной рукой, концентрированный подъем на бицепс",
        "reps": "3-4 по 12-15"
    },
    "preset_sat": {
        "day": "Суббота",
        "title": "Грудь и ноги (микс)",
        "ex": "Широкие отжимания, кубковые приседания (гантель у груди), подъем на носки",
        "reps": "3-4 по 15"
    },
    "preset_sun": {
        "day": "Воскресенье",
        "title": "Активное восстановление",
        "ex": "Растяжка всех групп мышц + легкая прогулка",
        "reps": "20-30 минут"
    }
}

def get_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📋 Готовые варианты по дням", "callback_data": "open_presets"}],
            [{"text": "⚙️ Таймер отдыха: 60 сек", "callback_data": "disabled_btn"}]
        ]
    }

def get_presets_keyboard():
    buttons = []
    for key, data in PRESETS.items():
        buttons.append([{"text": f"📅 {data['day']}: {data['title']}", "callback_data": key}])
    buttons.append([{"text": "⬅️ Назад в меню", "callback_data": "back_to_menu"}])
    return {"inline_keyboard": buttons}

def send_telegram_request(api_url, method, payload):
    url = f"{api_url}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            response.read()
    except Exception:
        pass

# Точка входа в Cloudflare Workers на чистом Python
async def on_fetch(request, env, ctx):
    if request.method != "POST":
        from js import Response
        return Response.new("Method Not Allowed", status=405)
        
    token = env.TELEGRAM_TOKEN
    api_url = f"https://telegram.org{token}"
    
    body_text = await request.text()
    update = json.loads(body_text)
    
    # Обработка команды /start
    if "message" in update and "text" in update["message"]:
        message = update["message"]
        chat_id = message["chat"]["id"]
        if message["text"] == "/start":
            send_telegram_request(api_url, "sendMessage", {
                "chat_id": chat_id,
                "text": "Привет! Я твой фитнес-напарник. Выбери раздел:",
                "reply_markup": get_main_keyboard()
            })
            
    # Обработка инлайн-кнопок
    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        
        if data == "open_presets":
            send_telegram_request(api_url, "editMessageText", {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": "📋 Выбери день недели для запуска готовой тренировки:",
                "reply_markup": get_presets_keyboard()
            })
            
        elif data == "back_to_menu":
            send_telegram_request(api_url, "editMessageText", {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": "Привет! Я твой фитнес-напарник. Выбери раздел:",
                "reply_markup": get_main_keyboard()
            })
            
        elif data.startswith("preset_"):
            preset_data = PRESETS.get(data)
            if preset_data:
                start_btn = {
                    "inline_keyboard": [
                        [{"text": "⏳ Засечь 60 сек отдыха", "callback_data": "alert_timer"}],
                        [{"text": "⬅️ Назад к дням недели", "callback_data": "open_presets"}]
                    ]
                }
                text = f"🎯 День: *{preset_data['day']}*\n💪 Тренировка: *{preset_data['title']}*\n\n📋 Упражнения:\n_{preset_data['ex']}_\n\n📊 Схема: *{preset_data['reps']}*"
                send_telegram_request(api_url, "editMessageText", {
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "reply_markup": start_btn
                })
                
        elif data == "alert_timer":
            send_telegram_request(api_url, "answerCallbackQuery", {
                "callback_query_id": callback["id"],
                "text": "⏳ Время пошло! Засеките 60 секунд отдыха. Отличный подход!",
                "show_alert": True
            })
            send_telegram_request(api_url, "sendMessage", {
                "chat_id": chat_id,
                "text": "🔔 Время пошло. Сделайте глубокий вдох и приготовьтесь к следующему подходу!"
            })

    from js import Response
    return Response.new(json.dumps({"ok": True}), status=200, headers={"Content-Type": "application/json"})
