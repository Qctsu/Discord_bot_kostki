# https://discord.com/api/oauth2/authorize?client_id=1158433425569624074&permissions=11264&scope=bot

# Importowanie niezbędnych modułów
import datetime
import os
import re
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
from nextcord import Embed
from Systems.two_d_twenty import roll_k6, roll_k20, handle_reaction_add  # Importowanie funkcji

# Wczytywanie zmiennych środowiskowych z pliku .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Słownik przechowujący czasy aktywacji systemów dla kanałów
active_systems = {}

# Konfiguracja intencji bota
intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!', intents=intents)


# Obsługa zdarzenia on_ready
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')


# Komenda "!2d20 x" na aktywację systemu 2d20 gdzie x to ilość godzin aktywacji systemu
@bot.command(name='2d20')
async def two_d_twenty(ctx, duration: int):
    """Aktywuje System 2d20 na określoną liczbę godzin."""
    end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration)
    active_systems[ctx.channel.id] = {'system': '2d20', 'end_time': end_time}

    # Tworzenie i wysyłanie embeda
    embed = Embed(
        title="System 2d20 aktywny",
        description=f"System **2d20** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**.",
        color=0x3498db  # Kolor embeda
    )
    await ctx.send(embed=embed)


# Komenda !clearsystems do czyszczenia aktywności wszystkich systemó
@bot.command()
async def clearsystems(ctx):
    """Czyści wszystkie aktywne systemy."""
    active_systems.clear()  # Czyszczenie wszystkich aktywnych systemów

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

    # Sprawdzanie, czy system jest aktywny na kanale
    if message.channel.id in active_systems:
        system_info = active_systems[message.channel.id]
        if system_info['system'] == '2d20' and system_info['end_time'] > datetime.datetime.utcnow():

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

        elif system_info['end_time'] <= datetime.datetime.utcnow():
            del active_systems[message.channel.id]

    # on_message, aby komendy działały poprawnie
    await bot.process_commands(message)


# Obsługa zdarzenia on_reaction_add
@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    await handle_reaction_add(reaction, user, bot)


# obsługa błędów
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


# Uruchamianie bota
bot.run(TOKEN)