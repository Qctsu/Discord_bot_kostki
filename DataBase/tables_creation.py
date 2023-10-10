import aiosqlite
import config

async def create_table():
    async with aiosqlite.connect(config.get_database_path()) as db:
        cursor = await db.cursor()

        # Tworzenie tabeli active_systems, jeśli nie istnieje
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_systems (
                channel_id TEXT PRIMARY KEY,
                system_name TEXT,
                duration_hours INTEGER,
                clock_time TIMESTAMP,
                end_time TIMESTAMP
            )
        ''')

        # Tworzenie tabeli guild_timezones, jeśli nie istnieje
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_timezones (
                guild_id TEXT PRIMARY KEY,
                timezone TEXT
            )
        ''')

        await db.commit()