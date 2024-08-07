import aiosqlite
import config.db_config as db_config

async def set_timezone(user_id, timezone):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        await cursor.execute('''
            INSERT OR REPLACE INTO timezones (user_id, timezone)
            VALUES (?, ?)
        ''', (str(user_id), timezone))

        await db.commit()

async def get_timezone(user_id):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        await cursor.execute('SELECT timezone FROM timezones WHERE user_id = ?', (str(user_id),))
        result = await cursor.fetchone()

        return result[0] if result else None