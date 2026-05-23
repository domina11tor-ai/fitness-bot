import asyncio
import sqlite3
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Инициализация БД
def init_db():
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, xp INTEGER, weight REAL, level INTEGER)""")
    conn.commit()
    conn.close()

init_db()

# --- ФУНКЦИИ УРОВНЕЙ И ДОСТИЖЕНИЙ ---
def add_xp(user_id, amount):
    conn = sqlite3.connect("fitness_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT xp, level FROM users WHERE id = ?", (user_id,))
    data = cursor.fetchone()
    if not data:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, amount, 0, 1))
    else:
        new_xp = data[0] + amount
        new_lvl = 1 + (new_xp // 100) # Уровень каждые 100 XP
        cursor.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?", (new_xp, new_lvl, user_id))
    conn.commit()
    conn.close()

# --- ГЕНЕРАТОР МОТИВАЦИИ ---
MOTIVATION = [
    "Боль — это временно. Результат — навсегда!",
    "Твое тело может выдержать почти все. Это твой разум должен быть убежден.",
    "Не останавливайся, когда устал. Останавливайся, когда закончил!"
]

# --- НОВАЯ КЛАВИАТУРА МЕНЮ ---
def get_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Тренировка", callback_data="start_workout")
    kb.button(text="⚖️ Дневник веса", callback_data="weight_menu")
    kb.button(text="🎮 Игры и Квиз", callback_data="games_menu")
    kb.button(text="🏆 Достижения", callback_data="achievements")
    kb.button(text="💡 Мотивация/Факты", callback_data="motivation_fact")
    kb.button(text="⚙️ Настройки напоминаний", callback_data="set_reminder")
    kb.adjust(2)
    return kb.as_markup()
