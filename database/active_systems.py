import aiosqlite
from datetime import datetime, timedelta
import config.db_config as db_config


# Funkcja do dodawania aktywnego systemu do bazy danych
async def add_active_system(channel_id, system_name, duration_hours, activation_time, end_time):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Formatowanie daty, aby usunąć milisekundy
        formatted_activation_time = datetime.fromisoformat(activation_time).replace(microsecond=0).isoformat(' ')

        # Formatowanie clock_time, aby usunąć milisekundy
        formatted_clock_time = datetime.fromisoformat(activation_time).replace(microsecond=0).isoformat(' ')

        # Obliczanie end_time
        activation_datetime = datetime.fromisoformat(activation_time)
        end_time = (activation_datetime + timedelta(hours=duration_hours)).replace(microsecond=0).isoformat(' ')

        await cursor.execute('''
            INSERT INTO active_systems (channel_id, system_name, duration_hours, clock_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(channel_id), system_name, duration_hours, formatted_clock_time, end_time))

        await db.commit()


# Funkcja do usuwania aktywnego systemu z bazy danych
async def remove_active_system(channel_id):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        await cursor.execute('DELETE FROM active_systems WHERE channel_id = ?', (str(channel_id),))

        await db.commit()


# Funkcja do pobierania aktywnego systemu z bazy danych
async def get_active_system(channel_id):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        await cursor.execute('SELECT * FROM active_systems WHERE channel_id = ?', (str(channel_id),))
        result = await cursor.fetchone()

        if result:
            system_info = {
                'channel_id': result[0],
                'system_name': result[1],
                'duration_hours': result[2],
                'clock_time': result[3],
                'end_time': result[4]
            }

            # Sprawdzanie i ewentualna konwersja end_time na obiekt datetime, jeśli jest stringiem
            if isinstance(system_info['end_time'], str):
                system_info['end_time'] = datetime.strptime(system_info['end_time'], '%Y-%m-%d %H:%M:%S')

            return system_info
        else:
            return None


# Funkcja do dezaktywacji przeterminowanych systemów
async def deactivate_expired_systems():
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Najpierw pobrać channel_id wygasłych systemów
        sql_select_expired = '''
            SELECT channel_id FROM active_systems WHERE end_time < CURRENT_TIMESTAMP
        '''
        await cursor.execute(sql_select_expired)
        expired_channels = [row[0] for row in await cursor.fetchall()]

        # Następnie usuń sesje dla tych kanałów z tabeli game_sessions
        for channel_id in expired_channels:
            sql_delete_session = '''
                DELETE FROM game_sessions WHERE channel_id = ?
            '''
            await cursor.execute(sql_delete_session, (channel_id,))

        # Teraz możemy usunąć wygasłe systemy z tabeli active_systems
        sql_delete_expired = '''
            DELETE FROM active_systems WHERE end_time < CURRENT_TIMESTAMP
        '''
        await cursor.execute(sql_delete_expired)

        await db.commit()


async def delete_session_from_game_sessions(channel_id: str):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Usuń sesję z tabeli game_sessions
        await cursor.execute('''
            DELETE FROM game_sessions
            WHERE channel_id = ?
        ''', (channel_id,))

        await db.commit()


# Czyszczenie wszystkich systemów
async def clear_active_systems():
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Usuwanie wszystkich rekordów z tabeli active_systems
        await cursor.execute('DELETE FROM active_systems')

        # Usuwanie wszystkich rekordów z tabeli game_sessions
        await cursor.execute('DELETE FROM game_sessions')

        await db.commit()


async def initialize_session(channel_id, system_name, gm_id, gm_nick):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Dodaj wpis do tabeli game_sessions
        await cursor.execute('''
            INSERT INTO game_sessions (channel_id, system_name, gm_id, gm_nick)
            VALUES (?, ?, ?, ?)
        ''', (channel_id, system_name, gm_id, gm_nick))

        await db.commit()
