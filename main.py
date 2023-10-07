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
from Systems.SWAE import damage, test  # Importowanie funkcji

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

    # Dodawanie pól z opisem komend
    embed.add_field(name="!k6",
                    value="**Użycie**: !Xk6\n"
                          "- X - liczba rzutów kostką (np. !3k6 dla 3 rzutów)\n"
                          "Rzut jedną lub więcej kostkami k6, gdzie:\n"
                          "'1' to 1 punkt, \n"
                          "'2' to 2 punkty, \n"
                          "'3' i '4' to 0 punktów, \n"
                          "'5' i '6' to 1 punkt oraz Efekt.\n\n"
                          "**Przykład**: `!3k6` (3 rzuty k6)",
                    inline=False)

    embed.add_field(name="!k20",
                    value="**Użycie**: !Xk20;Y\n"
                          "- X - liczba rzutów kostką (np. !3k20 dla 3 rzutów)\n"
                          "- Y - próg sukcesu\n"
                          "Rzut jedną lub więcej kostkami k20, gdzie: \n"
                          "każdy wynik równy lub niższy Y jest sukcesem. \n"
                          "'1' to krytyczny sukces (2 sukcesy), \n"
                          "'20' to komplikacja (porażka).\n\n"
                          "**Przykład**: `!3k20;12` (3 rzuty k20, próg sukcesu 12)",
                    inline=False)

    await ctx.send(embed=embed)

@bot.command(name='SWAE')
async def swae(ctx, duration: int):
    """Aktywuje System SWAE na określoną liczbę godzin."""
    end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration)
    active_systems[ctx.channel.id] = {'system': 'SWAE', 'end_time': end_time}

    embed = Embed(
        title="System SWAE aktywny",
        description=f"System **SWAE** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**.",
        color=0x3498db  # Kolor embeda
    )

    # Dodawanie pól z opisem komend
    embed.add_field(name="!test", value="**Użycie**: !test XkY(+Z/-Z)\n"
                                        "- X - Opcjonalna liczba rzutów kostką (domyślnie 1)\n"
                                        "- Y - Typ kostki (np. 6 dla k6, 10 dla k10, itp.)\n"
                                        "- (+Z/-Z) - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                                        "Rzuty kostką typu Y. Jeśli X = 1, dodatkowo rzuca kością figury (k6) i zwraca lepszy wynik.\n"
                                        "\n**Przykład**: `!test k8+2` (1 rzut k8 plus modyfikator +2)",
                    inline=False)

    embed.add_field(name="!damage", value="**Użycie**: !damage kY;Z(+A/-A)\n"
                                          "- Y - Typ pierwszej kostki (np. 6 dla k6, 12 dla k12, itp.)\n"
                                          "- Z - Opcjonalna, dodatkowa kostka, może być powtarzana wielokrotnie (np. ;8;4 dla dodatkowych rzutów k8 i k4)\n"
                                          "- (+A/-A) - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                                          "Rzuty kostkami określonymi przez Y oraz opcjonalne Z, a następnie sumuje wyniki i dodaje/odejmuje modyfikator.\n"
                                          "\n**Przykład**: `!damage k12;6;6+2` (Rzuty k12, k6, k6, suma plus modyfikator +2)",
                    inline=False)

    await ctx.send(embed=embed)


# Komenda !clearsystems do czyszczenia aktywności wszystkich systemów
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

        # System 2d20
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

        # System SWAE
        elif system_info['system'] == 'SWAE' and system_info['end_time'] > datetime.datetime.utcnow():
            # Logika dla testów
            test_match = re.match(r'!test (\d*)k(\d+)([+\-]\d+)?', message.content)

            # Logika dla obrażeń
            damage_match = re.match(r'!damage (?:k)?(\d+)(?:;(?:k)?(\d+))*(?:([+\-])\d+)?', message.content)

            if test_match:
                embed = await test(message.content, message.author.display_name)
                if embed:  # Jeśli embed nie jest None, wysyłamy go
                    await message.channel.send(embed=embed)

            elif damage_match:
                embed = await damage(message.content, message.author.display_name)
                if embed:
                    await message.channel.send(embed=embed)

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