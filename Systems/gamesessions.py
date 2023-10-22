from nextcord.ext import commands
from nextcord import Embed
from DataBase.active_systems import get_active_system
import db_config
import aiosqlite


class GameSessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gram(self, ctx):
        """Dodaje gracza do aktywnej sesji."""

        # Sprawdź, czy jakikolwiek system jest już aktywny na tym kanale
        existing_system = await get_active_system(ctx.channel.id)
        if not existing_system:
            embed = Embed(
                title="Błąd",
                description="Nie ma aktywnego systemu na tym kanale.",
                color=0xe74c3c  # Czerwony kolor embeda
            )
            await ctx.send(embed=embed)
            return

        # Sprawdź, czy gracz jest już w sesji
        is_already_playing = await check_player_in_session(ctx.channel.id, ctx.author.id)
        if is_already_playing:
            embed = Embed(
                title="Info",
                description="Już bierzesz udział w tej sesji.",
                color=0xf39c12  # Pomarańczowy kolor embeda
            )
            await ctx.send(embed=embed)
            return

        # Dodaj gracza do sesji
        await add_player_to_session(ctx.channel.id, ctx.author.id, ctx.author.display_name)

        embed = Embed(
            title="Dodano",
            description=f"Gracz {ctx.author.display_name} dołączył do sesji.",
            color=0x2ecc71  # Zielony kolor embeda
        )
        await ctx.send(embed=embed)


async def check_player_in_session(channel_id, player_id):
    """Sprawdza, czy gracz jest już w sesji."""
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()
        await cursor.execute('''
            SELECT COUNT(*) FROM game_sessions WHERE channel_id = ? AND player_id = ?
        ''', (channel_id, player_id))
        (count,) = await cursor.fetchone()
        return count > 0


async def add_player_to_session(channel_id, player_id, player_nick):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()

        # Znajdź istniejący rekord sesji na podstawie channel_id
        await cursor.execute('''
            SELECT session_id FROM game_sessions WHERE channel_id = ? AND active = TRUE
        ''', (channel_id,))
        session = await cursor.fetchone()

        if session:
            # Jeśli rekord sesji istnieje, dodaj nowego gracza do tabeli session_players
            await cursor.execute('''
                INSERT INTO session_players (session_id, player_id, player_nick)
                VALUES (?, ?, ?)
            ''', (session[0], player_id, player_nick))

            await db.commit()
        else:
            # Jeśli nie ma takiej sesji, możesz podjąć odpowiednie działania (np. wygenerować błąd)
            pass
