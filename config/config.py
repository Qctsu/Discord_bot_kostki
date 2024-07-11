import os
from pathlib import Path

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands


# Ścieżka do katalogu config relatywnie do bieżącego pliku
env_path = Path('config') / '.env'

# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Konfiguracja intencji bota
intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

# Uzyskujemy ścieżkę do bazy danych
database_path = db_config.get_database_path()

# Inicjalizacja bota
bot = commands.Bot(command_prefix=['!', '/'], intents=intents, help_command=None)
