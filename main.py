import asyncio
import datetime
import os
import re
from pathlib import Path

import aiosqlite
from dotenv import load_dotenv
from langdetect import detect
import nextcord
from nextcord import Embed
from nextcord.ext import commands, tasks
from nextcord.ui import Select, View

import config.db_config as db_config
import database.tables_creation as tables_creation
from database.active_systems import (clear_active_systems, deactivate_expired_systems, get_active_system, remove_active_system)
from bot_commands.bot_tools.setting_commands import TimeZone
from bot_commands.entertainment.systems.additional.add_to_game_session import GameSessions
from src.commands.systems.parser.neutral import generate_embed
from src.commands.systems.swae.SWAE import damage, test, handle_reaction_add_SWAE
from src.commands.systems.swae.SWAE_fight import Combat
from src.commands.systems.two_d_twenty.two_d_twenty import roll_k6, roll_k20, handle_reaction_add_2d20
from bot_commands.info.help_description import get_help_message

# Uzyskujemy ścieżkę do bazy danych
database_path = db_config.get_database_path()
print(f"Ścieżka do bazy danych: {database_path}")

# Ścieżka do katalogu config relatywnie do bieżącego pliku
env_path = Path('config') / '.env'

# Wczytywanie zmiennych środowiskowych z pliku .env znajdującego się w katalogu config
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Konfiguracja intencji bota
intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix=['!', '/'], intents=intents, help_command=None)

# Dodanie Cog z komendą settimezone
bot.add_cog(TimeZone(bot))
bot.add_cog(GameSessions(bot))
bot.add_cog(Combat(bot))


async def check_and_deactivate_systems():
    while True:
        print("Sprawdzam i deaktywuje wygasłe systemy...")
        await deactivate_expired_systems()
        await asyncio.sleep(60 * 30)  # Spanko na 30 minut


async def async_deactivate_expired_systems():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, deactivate_expired_systems)


# Słownik do przechowywania ostatnich komend użytkowników do przerzutu
user_last_commands = {}


# Obsługa zdarzenia on_ready
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

    await tables_creation.create_table()
    print(f'Tabela (jeśli nie istniała) została utworzona')

    bot.load_extension('bot_commands.entertainment.systems.additional.active_system_description')
    print(f'Pakiet systemów załadowany')

    bot.loop.create_task(check_and_deactivate_systems())

    print(f'Sprawdzanie usunięć z gildii')
    check_removal_dates.start()


async def get_inviter(guild):
    try:
        # Pobieramy wpisy z dziennika audytu dotyczące dodania bota
        audit_logs = await guild.audit_logs(action=nextcord.AuditLogAction.bot_add).flatten()

        # Spróbuj znaleźć najnowszy wpis, który odnosi się do dodania Twojego bota
        for entry in audit_logs:
            if entry.target.id == bot.user.id:
                return entry.user

        # Jeśli nie znaleziono wpisu, zwróć None
        return None

    except Exception as e:
        print(f"Wystąpił błąd podczas próby uzyskania osoby zapraszającej bota na serwer {guild.name}. Błąd: {e}")
        return None


@bot.event
async def on_guild_join(guild):
    # Pobierz kilka ostatnich wiadomości z najbardziej aktywnego kanału
    # Zakładam, że pierwszy dostępny kanał tekstowy to "najbardziej aktywny"
    channel = next((x for x in guild.channels if
                    isinstance(x, nextcord.TextChannel) and x.permissions_for(guild.me).read_messages), None)

    if channel:
        messages = await channel.history(limit=50).flatten()
        text_sample = " ".join([msg.content for msg in messages])

        # Wykrywanie języka
        detected_language = detect(text_sample)

        # Sprawdzenie, czy to język polski
        if detected_language == "pl":
            lang = "pl"
        else:
            lang = "eng"  # Można tu dodać więcej warunków dla innych języków

        # Dodanie wykrytego języka do tabeli konfiguracyjnej
        async with aiosqlite.connect(database_path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                '''INSERT OR IGNORE INTO server_config (guild_id, language, localization, roll_localization) VALUES (?, ?, ?, ?)''',
                (guild.id, lang, lang, lang))
            await db.commit()
            await cursor.close()

        # Wysłanie wiadomości DM do osoby, która dodała bota
        inviter = await get_inviter(guild)
        print(f"Inviter: {inviter}")  # Sprawdź, czy uzyskujesz prawidłowego zapraszającego

        if inviter is None:
            print("Nie udało się uzyskać osoby zapraszającej bota.")  # Upewnij się, że ta linia nie jest wydrukowywana
            return

        await inviter.send(
            f"Wykryłem, że dominujący język na serwerze to {lang}. Język został dodany do konfiguracji. Proszę o dalszą konfigurację.")
        print("Wiadomość DM wysłana!")  # Upewnij się, że ta linia jest wydrukowywana


class LanguageSelect(Select):
    def __init__(self):
        options = [
            nextcord.ui.SelectOption(label="Polski", value="PL"),
            nextcord.ui.SelectOption(label="English", value="ENG")
        ]
        super().__init__(placeholder='Wybierz język...', options=options)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(f"Wybrano język: {self.values[0]}")
        # Można tutaj dodać aktualizację języka w bazie danych


@bot.command(name='config', aliases=['konfiguracja'])
async def config(ctx, action=None, setting_name=None, value=None):
    # Usuń wiadomość z komendą
    try:
        await ctx.message.delete()
    except nextcord.errors.Forbidden:
        # Bot nie ma uprawnień do usuwania wiadomości
        pass

    # Upewnij się, że osoba wykonująca komendę ma odpowiednie uprawnienia
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.author.send("Nie masz wystarczających uprawnień do modyfikacji konfiguracji!")
        return

    async with aiosqlite.connect(database_path) as db:
        cursor = await db.cursor()

        if action is None:
            # Rozpocznij proces konfiguracji

            embed = Embed(title="Konfiguracja", description="Wybierz język bota:")
            view = View()
            view.add_item(LanguageSelect())

            await ctx.author.send(embed=embed, view=view)

        if action == "show":
            await cursor.execute("SELECT * FROM server_config WHERE guild_id = ?", (ctx.guild.id,))
            config_data = await cursor.fetchone()
            if config_data:
                # Formatujemy dane, aby były czytelne
                columns = [desc[0] for desc in cursor.description]
                config_message = "\n".join([f"{column}: {value}" for column, value in zip(columns, config_data)])
                await ctx.author.send(f"Konfiguracja serwera:\n{config_message}")
            else:
                await ctx.author.send("Konfiguracja dla tego serwera nie istnieje.")
        # Modyfikowanie konfiguracji dodamy później
        # ...

        # Zamykamy kursor
        await cursor.close()

@bot.command(name='rzuc', aliases=['r'], help='Rzuć kostkami według podanej specyfikacji. Użycie: !rzuc 2k6+2 3k100+10 5k10-2')
async def rzuc(ctx, *, dice_expression: str):
    embed = generate_embed(dice_expression, ctx.author.display_name)
    await ctx.send(embed=embed)

@bot.command(name='help', help='Pokazuje tę wiadomość')
async def custom_help(ctx):
    help_message = get_help_message(bot.command_prefix)  # Wywołanie funkcji do uzyskania opisu komend
    await ctx.author.send(help_message)  # Wysyłanie opisu komend na DM użytkownika
    await ctx.send(f"{ctx.author.mention}, wysłałem Ci listę komend na DM!")  # Opcjonalne potwierdzenie na kanale


# Komenda !clearsystems do czyszczenia aktywności wszystkich systemów
@bot.command()
async def clearsystems(ctx):
    """Czyści wszystkie aktywne systemy."""
    # Czyszczenie wszystkich aktywnych systemów w bazie danych
    await clear_active_systems()  # WYWOŁANIE NOWEJ FUNKCJI
    # Tworzenie i wysyłanie embeda
    embed = Embed(
        title="Systemy dezaktywowane",
        description=f"Wszystkie systemy zostały dezaktywowane.",
        color=0x3498db  # Kolor embeda
    )
    await ctx.send(embed=embed)


# Obsługa zdarzenia on_message
@bot.event
async def on_message(message):
    # Jeśli wiadomość pochodzi od bota, ignorujemy ją
    if message.author == bot.user:
        return

    # Sprawdzanie, czy system jest aktywny na kanale w bazie danych
    system_info = await get_active_system(message.channel.id)

    if system_info:
        # Obliczanie czasu aktywacji systemu
        current_time = datetime.datetime.utcnow()

        if system_info['end_time'] <= current_time:
            # Czas aktywności systemu minął, usuwamy go z bazy danych
            remove_active_system(message.channel.id)

        elif system_info['end_time'] > current_time:
            # Wywołanie odpowiednich funkcji w zależności od systemu
            await process_system_commands(system_info, message)

    # on_message, aby komendy działały poprawnie
    await bot.process_commands(message)


async def process_system_commands(system_info, message):
    """
    Funkcja obsługująca komendy systemowe.
    """
    # System 2d20
    if system_info['system_name'] == '2d20':
        await process_2d20_commands(message)
    # System SWAE
    elif system_info['system_name'] == 'SWAE':
        await process_SWAE_commands(message)


async def process_2d20_commands(message):
    # Logika dla rzutów kostką
    k6_match = re.match(r'!(\d*)k6', message.content)
    k20_match = re.match(r'!(\d*)k20;(\d+)', message.content)

    if k6_match:
        embed = roll_k6(message.content, message.author.display_name)
        await message.channel.send(embed=embed)

    elif k20_match:
        embed, num_dice = roll_k20(message.content, message.author.display_name)
        msg = await message.channel.send(embed=embed)
        for i in range(num_dice):
            await msg.add_reaction(f"{chr(0x1F1E6 + i)}")  # Dodawanie reakcji A-Z
        await msg.add_reaction('🔄')  # Dodawanie reakcji przerzutu
        await msg.add_reaction('❌')  # Dodajemy reakcję anulowania przerzutów


async def process_SWAE_commands(message):
    # Tutaj umieść logikę dla systemu SWAE
    # Logika dla testów
    test_match = re.match(r'!(test|t) (\d*)k(\d+)([+\-]\d+)?', message.content)

    # Logika dla obrażeń
    damage_match = re.match(r'!(damage|d|o) (?:k)?(\d+)(?:;(?:k)?(\d+))*(?:([+\-])\d+)?', message.content)

    if test_match:
        user_id = message.author.display_name
        command = message.content

        result = await test(message.content, message.author.display_name)
        if result:  # Jeśli wynik nie jest None, przetwarzamy go
            embed, can_reroll = result  # Rozpakowujemy krotkę
            msg = await message.channel.send(embed=embed)  # Wysyłamy embed

            message_id = msg.id
            add_user_command(message_id, user_id, command)

            if can_reroll:  # Jeśli can_reroll jest True, dodajemy reakcję
                await msg.add_reaction('🔄')
            await msg.add_reaction('❌')  # Dodajemy reakcję anulowania przerzutów
    elif damage_match:
        embed = await damage(message.content, message.author.display_name)
        if embed:
            await message.channel.send(embed=embed)


# Obsługa zdarzenia on_reaction_add
@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    # Pobieranie ID kanału, na którym dodano reakcję
    channel_id = reaction.message.channel.id

    # Sprawdzanie, czy kanał jest w bazie danych jako aktywny system
    system_info = await get_active_system(channel_id)

    if system_info:
        # Sprawdzanie, czy czas aktywności systemu nie upłynął
        if system_info['end_time'] >= datetime.datetime.utcnow():

            # Wywołanie odpowiedniej funkcji w zależności od aktywnego systemu
            if system_info['system_name'] == '2d20':
                await handle_reaction_add_2d20(reaction, user, bot)

            elif system_info['system_name'] == 'SWAE':
                await handle_reaction_add_SWAE(reaction, user, bot, user_last_commands)

        # Jeśli czas aktywności systemu upłynął, usuwamy wpis ze słownika
        else:
            await remove_active_system(channel_id)

@bot.event
async def on_guild_remove(guild):
    removal_date = datetime.datetime.utcnow()
    async with aiosqlite.connect(database_path) as db:
        cursor = await db.cursor()
        await cursor.execute('''UPDATE server_config SET removal_date = ? WHERE guild_id = ?''',
                             (removal_date, guild.id))
        await db.commit()
        await cursor.close()

@tasks.loop(hours=24)  # Sprawdzanie co 24 godziny
async def check_removal_dates():
    current_date = datetime.datetime.utcnow()
    async with aiosqlite.connect(database_path) as db:
        cursor = await db.cursor()
        await cursor.execute('''SELECT guild_id, removal_date FROM server_config WHERE removal_date IS NOT NULL''')
        rows = await cursor.fetchall()

        for row in rows:
            removal_date = datetime.datetime.fromisoformat(row[1])  # Zakładając, że data jest zapisywana w formacie ISO
            if (current_date - removal_date).days >= 7:  # Jeżeli minął tydzień
                await cursor.execute('''DELETE FROM server_config WHERE guild_id = ?''', (row[0],))

        await db.commit()
        await cursor.close()


# obsługa błędów
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

def add_user_command(message_id, user_id, command):
    user_last_commands[message_id] = {"user_id": user_id, "command": command}

bot.load_extension('bot_commands.entertainment.music.music')
# Uruchamianie bota
bot.run(TOKEN)