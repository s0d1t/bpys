import aiosqlite

# Инициализация базы данных (создание таблиц)
async def init_db():
    async with aiosqlite.connect("bot_data.db") as db:
        # Создаем таблицу для хранения пользователей, их ников и варнов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                warns INTEGER DEFAULT 0
            )
        """)
        await db.commit()

# Функция для обновления данных пользователя (когда он пишет сообщение)
async def update_user(user_id, username):
    async with aiosqlite.connect("bot_data.db") as db:
        # Переводим username в нижний регистр для удобного поиска
        username_lower = username.lower() if username else None
        
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, warns) "
            "VALUES (?, ?, (SELECT warns FROM users WHERE user_id = ?))",
            (user_id, username_lower, user_id)
        )
        await db.commit()

# Функция добавления варна
async def add_warn(user_id):
    async with aiosqlite.connect("bot_data.db") as db:
        await db.execute("UPDATE users SET warns = warns + 1 WHERE user_id = ?", (user_id,))
        async with db.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            await db.commit()
            return row[0] if row else 0

# Функция поиска ID по юзернейму (для команд типа /ban @username)
async def get_id_by_username(username):
    async with aiosqlite.connect("bot_data.db") as db:
        # Убираем @ если пользователь его ввел
        clean_username = username.replace("@", "").lower()
        async with db.execute("SELECT user_id FROM users WHERE username = ?", (clean_username,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None