import aiosqlite

async def init_db():
    async with aiosqlite.connect("bot_data.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                warns INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def update_user(user_id, username):
    async with aiosqlite.connect("bot_data.db") as db:
        username_lower = username.lower() if username else None
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, warns) "
            "VALUES (?, ?, (SELECT warns FROM users WHERE user_id = ?))",
            (user_id, username_lower, user_id)
        )
        await db.commit()

async def add_warn(user_id):
    async with aiosqlite.connect("bot_data.db") as db:
        await db.execute("UPDATE users SET warns = warns + 1 WHERE user_id = ?", (user_id,))
        async with db.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            await db.commit()
            return row[0] if row else 0

async def get_id_by_username(username):
    async with aiosqlite.connect("bot_data.db") as db:
        clean_username = username.replace("@", "").lower()
        async with db.execute("SELECT user_id FROM users WHERE username = ?", (clean_username,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None