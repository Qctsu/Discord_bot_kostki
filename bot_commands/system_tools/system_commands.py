from nextcord.ext import commands
import datetime
from nextcord import Embed


class SystemCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Słownik przechowujący czasy aktywacji systemów dla kanałów
        self.active_systems = {}
        self.system_messages_sent = {}  # Nowa zmienna śledząca, czy wiadomość została już wysłana

    async def send_system_message(self, ctx, system_name, duration):
        # Sprawdza, czy wiadomość już została wysłana
        if str(ctx.channel.id) in self.system_messages_sent:
            return

        end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=duration)
        self.active_systems[str(ctx.channel.id)] = {'system': system_name, 'end_time': end_time}

        # Tworzenie i wysyłanie embeda tylko raz
        embed = Embed(
            title=f"System {system_name} aktywny",
            description=f"System **{system_name}** został aktywowany na kanale **{ctx.channel.name}** na **{duration} godzin(y)**.",
            color=0x3498db  # Kolor embeda
        )

        # Dodawanie pól z opisem komend
        if system_name == '2d20':
            embed.add_field(name="!k6",
                            value="**Użycie**: !Xk6\n"
                                  "- X - liczba rzutów kostką (np. !3k6 dla 3 rzutów)\n"
                                  "Rzut jedną lub więcej kostkami k6, gdzie '1' to 1 punkt, '2' to 2 punkty, '3' i '4' to 0 punktów, a '5' i '6' to 1 punkt oraz Efekt.\n"
                                  "\n**Przykład**: `!3k6` (3 rzuty k6)",
                            inline=False)

            embed.add_field(name="!k20",
                            value="**Użycie**: !Xk20;Y\n"
                                  "- X - liczba rzutów kostką (np. !3k20 dla 3 rzutów)\n"
                                  "- Y - próg sukcesu\n"
                                  "Rzut jedną lub więcej kostkami k20, gdzie każdy wynik równy lub niższy Y jest sukcesem. '1' to krytyczny sukces (2 sukcesy), '20' to komplikacja (porażka).\n"
                                  "\n**Przykład**: `!3k20;12` (3 rzuty k20, próg sukcesu 12)",
                            inline=False)
        elif system_name == 'SWAE':
            embed.add_field(name="!test", value="**Użycie**: !test [X]kY[+Z/-Z]\n"
                                                "- [X] - Opcjonalna liczba rzutów kostką (domyślnie 1)\n"
                                                "- Y - Typ kostki (np. 6 dla k6, 10 dla k10, itp.)\n"
                                                "- [+Z/-Z] - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                                                "Rzuty kostką typu Y. Jeśli [X] = 1, dodatkowo rzuca kością figury (k6) i zwraca lepszy wynik.\n"
                                                "\n**Przykład**: `!test k8+2` (1 rzut k8 plus modyfikator +2)",
                            inline=False)

            embed.add_field(name="!damage", value="**Użycie**: !damage Y[;Z][+A/-A]\n"
                                                  "- Y - Typ pierwszej kostki (np. 6 dla k6, 12 dla k12, itp.)\n"
                                                  "- [;Z] - Opcjonalna, dodatkowa kostka, może być powtarzana wielokrotnie (np. ;8;4 dla dodatkowych rzutów k8 i k4)\n"
                                                  "- [+A/-A] - Opcjonalny modyfikator, który zostanie dodany/odjęty od wyniku\n"
                                                  "Rzuty kostkami określonymi przez Y oraz opcjonalne Z, a następnie sumuje wyniki i dodaje/odejmuje modyfikator.\n"
                                                  "\n**Przykład**: `!damage 12;6;6+2` (Rzuty k12, k6, k6, suma plus modyfikator +2)",
                            inline=False)

        await ctx.send(embed=embed)

        # Oznaczamy kanał jako już aktywowany
        self.system_messages_sent[str(ctx.channel.id)] = True

    @commands.command(name='2d20')
    async def two_d_twenty(self, ctx, duration: int):
        """Aktywuje System 2d20 na określoną liczbę godzin."""
        await self.send_system_message(ctx, '2d20', duration)

    @commands.command(name='SWAE')
    async def swae(self, ctx, duration: int):
        """Aktywuje System SWAE na określoną liczbę godzin."""
        await self.send_system_message(ctx, 'SWAE', duration)

    @commands.command()
    async def clearsystems(self, ctx):
        """Czyści wszystkie aktywne systemy."""
        self.active_systems.clear()
        self.system_messages_sent.clear()  # Usuwamy informacje o wysłanych wiadomościach
        # [Pozostała logika komendy]
        # Tworzenie i wysyłanie embeda
        embed = Embed(
            title="Systemy dezaktywowane",
            description=f"Wszystkie systemy zostały dezaktywowane.",
            color=0x3498db  # Kolor embeda
        )
        await ctx.send(embed=embed)
        self.bot.active_systems.clear()


# Funkcja pomocnicza do łatwego dodawania komend do bota
def setup(bot):
    bot.add_cog(SystemCommands(bot))
