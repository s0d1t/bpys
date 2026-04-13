import os
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import database as db_logic

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ПРОВЕРКИ И УТИЛИТЫ ---
async def check_admin(message: types.Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await message.reply("❌ Ошибка: Вы не администратор!")
        return False
    return True

async def get_target(message: types.Message, command_args: str):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.full_name
    if command_args and command_args.startswith("@"):
        user_id = await db_logic.get_id_by_username(command_args)
        if user_id: return user_id, command_args
    return None, None

def get_time_arg(args: str):
    if not args: return None
    for part in args.split():
        if part.isdigit(): return int(part)
    return None

# --- КЛАВИАТУРЫ ---
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Инструкция", callback_data="instruction")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="start_menu")]])

# --- ОБРАБОТЧИКИ МЕНЮ ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот-модератор. Выбери действие:", reply_markup=start_kb())

@dp.callback_query(F.data == "start_menu")
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=start_kb())

@dp.callback_query(F.data == "about")
async def about_us(callback: CallbackQuery):
    await callback.message.edit_text("🛡 Бот бесплатный и помогает админам.", reply_markup=back_kb())

@dp.callback_query(F.data == "instruction")
async def show_inst(callback: CallbackQuery):
    await callback.message.edit_text("Добавь меня в чат и дай права админа.\nКоманды: /ban, /mute, /warn", reply_markup=back_kb())

# --- КОМАНДЫ МОДЕРАЦИИ ---
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def track(msg: types.Message):
    await db_logic.update_user(msg.from_user.id, msg.from_user.username)

@dp.message(Command("warn"))
async def cmd_warn(message: types.Message, command: Command):
    if not await check_admin(message): return
    tid, tname = await get_target(message, command.args)
    if tid:
        w = await db_logic.add_warn(tid)
        if w >= 3:
            await message.chat.ban(user_id=tid)
            await message.answer(f"🔴 {tname} забанен (3/3 варнов).")
        else:
            await message.answer(f"⚠️ {tname}: варн {w}/3")

@dp.message(Command("mute"))
async def cmd_mute(message: types.Message, command: Command):
    if not await check_admin(message): return
    tid, tname = await get_target(message, command.args)
    if tid:
        m = get_time_arg(command.args) or 60
        until = datetime.now() + timedelta(minutes=m)
        await message.chat.restrict(tid, permissions=ChatPermissions(can_send_messages=False), until_date=until)
        await message.answer(f"🔇 {tname} в муте на {m} мин.")

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message, command: Command):
    if not await check_admin(message): return
    tid, tname = await get_target(message, command.args)
    if tid:
        d = get_time_arg(command.args)
        if d:
            await message.chat.ban(user_id=tid, until_date=datetime.now() + timedelta(days=d))
            await message.answer(f"🚫 {tname} в бане на {d} дн.")
        else:
            await message.chat.ban(user_id=tid)
            await message.answer(f"💀 {tname} забанен навсегда.")

@dp.message(Command("unban"))
async def cmd_unban(message: types.Message, command: Command):
    if not await check_admin(message): return
    tid, tname = await get_target(message, command.args)
    if tid:
        await message.chat.unban(tid, last_at_message=True)
        await message.answer(f"✅ {tname} разбанен.")

async def main():
    await db_logic.init_db()
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Меню"),
        types.BotCommand(command="warn", description="Варн"),
        types.BotCommand(command="mute", description="Мут"),
        types.BotCommand(command="ban", description="Бан")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())