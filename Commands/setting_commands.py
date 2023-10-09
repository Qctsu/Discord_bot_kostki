import asyncio
import nextcord
from nextcord.ext import commands
from DataBase.queries import set_timezone, get_timezone

class TimeZone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='settimezone')
    async def set_timezone(self, ctx):
        # Tutaj zdefiniuj listę dostępnych stref czasowych (np. z bazy danych lub ręcznie)
        timezones = [
            {
                "country": "Polska",
                "timezone": "UTC+1"
            },
            {
                "country": "USA",
                "timezone": "UTC-5"
            },
            # Dodaj inne kraje i strefy czasowe
        ]

        # Stwórz wiadomość prywatną dla użytkownika
        embed = nextcord.Embed(
            title="Wybierz strefę czasową:",
            description="Wybierz kraj i odpowiadającą mu strefę czasową:",
            color=nextcord.Color.blue()
        )

        # Dodaj rozwijalne pole wyboru dla krajów i stref czasowych
        for timezone_info in timezones:
            embed.add_field(
                name=timezone_info["country"],
                value=timezone_info["timezone"],
                inline=False
            )

        # Wyślij wiadomość prywatną z embedem
        await ctx.author.send(embed=embed)

        # Oczekuj na odpowiedź od użytkownika w wiadomości prywatnej
        def check(message):
            return message.author == ctx.author and message.guild is None

        try:
            response = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Czas na odpowiedź minął.")
            return

        selected_timezone = response.content.strip()

        if not selected_timezone:
            # Użytkownik nie wybrał strefy czasowej
            await ctx.author.send("Czas upłynął, a strefa czasowa nie została zmieniona.")
        else:
            # Użytkownik wybrał strefę czasową
            await set_timezone(ctx.author.id, selected_timezone)
            await ctx.author.send(f"Pomyślnie ustawiono strefę czasową na: {selected_timezone}")

def setup(bot):
    bot.add_cog(TimeZone(bot))
