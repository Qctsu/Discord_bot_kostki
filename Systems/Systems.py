import datetime
from nextcord.ext import commands
from nextcord import Embed

class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Zastąp poniższe `active_systems` Twoim mechanizmem śledzenia aktywnych systemów
        self.active_systems = {}

    async def activate_system(self, ctx, system_name: str, duration: int, embed_description: str, embed_fields: dict):
        # Sprawdź, czy jakikolwiek system jest już aktywny na tym kanale
        if ctx.channel.id in self.active_systems:
            # Jeśli tak, powiadom użytkownika i przerwij funkcję
            embed = Embed(
                title="Błąd",
                description=f"System **{self.active_systems[ctx.channel.id]['system']}** jest już aktywny na tym kanale. Czy na pewno chcesz go dezaktywować?",
                color=0xe74c3c  # Czerwony kolor embeda
            )
            await ctx.send(embed=embed)
            return

        end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration)
        self.active_systems[ctx.channel.id] = {'system': system_name, 'end_time': end_time}

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
            "!k6": ("**Użycie**: !Xk6\n"
                    "- X - liczba rzutów kostką (np. !3k6 dla 3 rzutów)\n"
                    "Rzut jedną lub więcej kostkami k6, gdzie:\n"
                    "'1' to 1 punkt, \n"
                    "'2' to 2 punkty, \n"
                    "'3' i '4' to 0 punktów, \n"
                    "'5' i '6' to 1 punkt oraz Efekt.\n\n"
                    "**Przykład**: `!3k6` (3 rzuty k6)"),
            "!k20": ("**Użycie**: !Xk20;Y\n"
                     "- X - liczba rzutów kostką (np. !3k20 dla 3 rzutów)\n"
                     "- Y - próg sukcesu\n"
                     "Rzut jedną lub więcej kostkami k20, gdzie: \n"
                     "każdy wynik równy lub niższy Y jest sukcesem. \n"
                     "'1' to krytyczny sukces (2 sukcesy), \n"
                     "'20' to komplikacja (porażka).\n\n"
                     "**Przykład**: `!3k20;12` (3 rzuty k20, próg sukcesu 12)")
        }
        await self.activate_system(ctx, '2d20', duration, description, fields)

    @commands.command(name='SWAE')
    async def swae(self, ctx, duration: int):
        description = f"System **SWAE** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**."
        fields = {
            "!test": ("**Użycie**: !test XkY(+Z/-Z)\n"
                      "- X - Opcjonalna liczba rzutów kostką (domyślnie 1)\n"
                      "- Y - Typ kostki (np. 6 dla k6, 10 dla k10, itp.)\n"
                      "- (+Z/-Z) - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                      "Rzuty kostką typu Y. Jeśli X = 1, dodatkowo rzuca kością figury (k6) i zwraca lepszy wynik.\n"
                      "\n**Przykład**: `!test k8+2` (1 rzut k8 plus modyfikator +2)"),
            "!damage": ("**Użycie**: !damage kY;Z(+A/-A)\n"
                        "- Y - Typ pierwszej kostki (np. 6 dla k6, 12 dla k12, itp.)\n"
                        "- Z - Opcjonalna, dodatkowa kostka, może być powtarzana wielokrotnie (np. ;8;4 dla dodatkowych rzutów k8 i k4)\n"
                        "- (+A/-A) - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                        "Rzuty kostkami określonymi przez Y oraz opcjonalne Z, a następnie sumuje wyniki i dodaje/odejmuje modyfikator.\n"
                        "\n**Przykład**: `!damage k12;6;6+2` (Rzuty k12, k6, k6, suma plus modyfikator +2)")
        }
        await self.activate_system(ctx, 'SWAE', duration, description, fields)

def setup(bot):
    bot.add_cog(Systems(bot))