import datetime
from nextcord.ext import commands
from nextcord import Embed
import asyncio
from DataBase.active_systems import add_active_system, remove_active_system, get_active_system


class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def activate_system(self, ctx, system_name: str, duration_hours: int, embed_description: str,
                              embed_fields: dict):

        # Przelicz czas z godzin na minuty
        duration_minutes = duration_hours * 60

        # Sprawdź, czy jakikolwiek system jest już aktywny na tym kanale
        existing_system = await get_active_system(ctx.channel.id)

        if existing_system:
            # Jeśli istnieje, powiadom użytkownika i przerwij funkcję
            embed = Embed(
                title="Błąd",
                description=f"System **{existing_system['system_name']}** jest już aktywny na tym kanale. Czy na pewno chcesz go dezaktywować?",
                color=0xe74c3c  # Czerwony kolor embeda
            )
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")  # Reakcja "check"
            await message.add_reaction("❌")  # Reakcja "x"

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:  # Jeśli czas minął, usuń wiadomość i przerwij funkcję
                await message.delete()
                return
            else:
                if str(reaction.emoji) == "✅":
                    await remove_active_system(ctx.channel.id)  # Usuń stary system
                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    return
            # Usuń wiadomość
            await message.delete()

        current_time = datetime.datetime.utcnow()
        end_time = current_time + datetime.timedelta(hours=duration_hours)

        formatted_activation_time = current_time.replace(microsecond=0).isoformat(' ')
        formatted_end_time = end_time.replace(microsecond=0).isoformat(' ')

        await add_active_system(ctx.channel.id, system_name, duration_hours, formatted_activation_time,
                                formatted_end_time)

        embed = Embed(
            title=f"System {system_name} aktywny",
            description=embed_description,
            color=0x3498db  # Kolor embeda
        )

        for field_name, field_value in embed_fields.items():
            embed.add_field(name=field_name, value=field_value, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='2d20')
    async def two_d_twenty(self, ctx, duration: int):
        description = f"System **2d20** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**."
        fields = {
            "!k6": (
                "**Użycie**: !Xk6\n"
                "- X - liczba rzutów kostką (np. !3k6 dla 3 rzutów)\n"
                "Rzut jedną lub więcej kostkami k6, gdzie:\n"
                "'1' to 1 punkt, \n"
                "'2' to 2 punkty, \n"
                "'3' i '4' to 0 punktów, \n"
                "'5' i '6' to 1 punkt oraz Efekt.\n"
                "**Przykład**: `!3k6` (3 rzuty k6)\n\n"
            ),
            "!k20": (
                "**Użycie**: !Xk20;Y[;F]\n"
                "- X - liczba rzutów kostką (np. !3k20 dla 3 rzutów)\n"
                "- Y - próg sukcesu\n"
                "- F (opcjonalne) - wartość fokusu\n"
                "Rzut jedną lub więcej kostkami k20, gdzie: \n"
                "każdy wynik równy lub niższy Y jest sukcesem. \n"
                "'1' to krytyczny sukces (2 sukcesy), \n"
                "'20' to komplikacja (porażka).\n"
                "Jeśli F jest dostępne, wyniki równe lub niższe F również są sukcesem.\n\n"
                "**Przykład bez fokusu**: `!3k20;12` (3 rzuty k20, próg sukcesu 12)\n"
                "**Przykład z fokusem**: `!3k20;12;5` (3 rzuty k20, próg sukcesu 12, fokus 5)\n\n"
                "Wsparcie merytoryczne: **piotrek_jay**\n"
                "Pomoc w rozwoju: **Alianora**\n"
                "Błędy w działaniu proszę zgłaszać do: **kucu**"
            )
        }
        await self.activate_system(ctx, '2d20', duration, description, fields)

    @commands.command(name='SWAE')
    async def swae(self, ctx, duration: int):
        description = f"System **SWAE** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**."
        fields = {
            "!(test|t)": (
                "**Użycie**: !(test|t) XkY(+Z/-Z)\n"
                "- !(test|t) - komenda do wykonania rzutu na test (można wpisać !test lub !t)\n"
                "- X - Opcjonalna liczba rzutów kostką (domyślnie 1)\n"
                "- Y - Typ kostki (np. 6 dla k6, 10 dla k10, itp.)\n"
                "- (+Z/-Z) - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                "Rzuty kostką typu Y, ilość kości X, dodatkowo rzuca kością figury (k6) i zwraca lepszy wynik.\n"
                "W teście mamy możliwość przerzutu używając reakcji 🔄 w odpowiedzi na rzut.\n"
                "**Przykład**: `!(test|t) 2k8+2` (2 rzut k8 plus modyfikator +2)\n\n"
            ),
            "!(damage|d|o)": (
                "**Użycie**: !(damage|d|o) kY;Z(+Z/-Z) lub !(damage|d|o) XkY(+Z/-Z)\n"
                "- !(damage|d|o) - komenda do wykonania rzutu na obrażenia (można wpisać !damage, !d lub !o)\n"
                "- X - Opcjonalna liczba rzutów kostką (domyślnie 1)\n"
                "- Y - Typ pierwszej kostki (np. 6 dla k6, 12 dla k12, itp.)\n"
                "- Z - Opcjonalna, dodatkowa kostka, może być powtarzana wielokrotnie (np. ;8;4 dla dodatkowych rzutów k8 i k4)\n"
                "- (+A/-A) - Opcjonalny modyfikator, który zostanie dodany/odejmuje wyniku\n"
                "Rzuty kostkami określonymi przez Y oraz opcjonalne Z, a następnie sumuje wyniki i dodaje/odejmuje modyfikator.\n"
                "lub\n"
                "Rzuty kostką typu Y, ilość kości X oraz opcjonalne Z, a następnie sumuje wyniki i dodaje/odejmuje modyfikator.\n"
                "**Przykład**: `!(damage|d|o) k12;6;6+2` (Rzuty k12, k6, k6, suma plus modyfikator +2)\n"
                "**Przykład 2**: `!(damage|d|o) 2k10+2` (2 rzuty k10 plus modyfikator +2)\n\n"
                "Wsparcie merytoryczne: **piotrek_jay**\n"
                "Błędy w działaniu proszę zgłaszać do: **kucu**"
            )
        }
        await self.activate_system(ctx, 'SWAE', duration, description, fields)


def setup(bot):
    bot.add_cog(Systems(bot))
