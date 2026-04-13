import os
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
import database as db_logic # Используем прошлый файл database.py

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРЫ ---

def get_start_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🚀 Подключить бота (инструкция)", callback_data="instruction")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="start_menu")]
    ])

# --- ОБРАБОТЧИКИ МЕНЮ ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я продвинутый бот-помощник для администраторов групп. "
        "Помогу навести порядок, усмирить нарушителей и автоматизировать модерацию.",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "start_menu")
async def back_to_start(callback: types.Callback_query):
    await callback.message.edit_text(
        "Главное меню бота-помощника:",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "about")
async def about_us(callback: types.Callback_query):
    await callback.message.edit_text(
        "🛡 **О проекте**\n\n"
        "Это полностью бесплатный бот, созданный для помощи администраторам Telegram-сообществ.\n"
        "Моя цель — сделать управление группой простым и эффективным.",
        reply_markup=get_back_keyboard()
    )

@dp.callback_query(F.data == "instruction")
async def show_instruction(callback: types.Callback_query):
    await callback.message.edit_text(
        "🛠 **Как подключить бота:**\n\n"
        "1. Добавьте бота в вашу группу/супергруппу.\n"
        "2. Назначьте бота **администратором**.\n"
        "3. Дайте ему права на удаление сообщений и блокировку пользователей.\n\n"
        "**Доступные команды (только для админов):**\n"
        "• `/warn` — выдать предупреждение (3 варна = бан)\n"
        "• `/mute [мин]` — запретить писать (по умолч. 60 мин)\n"
        "• `/ban [дни]` — забанить (пусто = навсегда)\n"
        "• `/unmute` / `/unban` — снять наказание",
        reply_markup=get_back_keyboard()
    )

# --- ЛОГИКА МОДЕРАЦИИ (БАН/МУТ/ВАРН) ---
# Тут остаются функции cmd_warn, cmd_mute, cmd_ban, которые мы писали раньше.
# Не забудь добавить проверку check_admin и отслеживание track_users.

async def main():
    await db_logic.init_db()
    # Регистрируем команды, чтобы они всплывали в подсказках
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="warn", description="Выдать варн"),
        types.BotCommand(command="mute", description="Замутить"),
        types.BotCommand(command="ban", description="Забанить"),
        types.BotCommand(command="unban", description="Разбанить")
    ])
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())