# Importowanie niezbędnych modułów
import DataBase.tables_creation as DB_kostki
from DataBase.active_systems import get_active_system, remove_active_system, deactivate_expired_systems, \
    clear_active_systems
import datetime
import os
import re
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
from nextcord import Embed
from Systems.two_d_twenty import roll_k6, roll_k20, handle_reaction_add_2d20  # Importowanie funkcji
from Systems.SWAE import damage, test, handle_reaction_add_SWAE  # Importowanie funkcji
import asyncio
from Commands.setting_commands import TimeZone

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Konfiguracja intencji bota
intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!', intents=intents)

# Dodanie Cog z komendą settimezone
bot.add_cog(TimeZone(bot))

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

    await DB_kostki.create_table()
    print(f'Tabela (jeśli nie istniała) została utworzona')

    bot.load_extension('Systems.Systems')
    print(f'Pakiet systemów załadowany')

    bot.loop.create_task(check_and_deactivate_systems())


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
    test_match = re.match(r'!test (\d*)k(\d+)([+\-]\d+)?', message.content)

    # Logika dla obrażeń
    damage_match = re.match(r'!damage (?:k)?(\d+)(?:;(?:k)?(\d+))*(?:([+\-])\d+)?', message.content)

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


# obsługa błędów
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


def add_user_command(message_id, user_id, command):
    user_last_commands[message_id] = {"user_id": user_id, "command": command}


# Uruchamianie bota
bot.run(TOKEN)
