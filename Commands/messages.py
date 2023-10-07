from nextcord.ext import commands
import datetime
import re
from Systems.two_d_twenty import roll_k6, roll_k20, handle_reaction_add
from Systems.SWAE import damage, test

class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Słownik przechowujący czasy aktywacji systemów dla kanałów
        self.active_systems = {}
        self.system_active = {}  # Słownik przechowujący informacje o tym, czy system jest aktywowany na danym kanale

    @commands.Cog.listener()
    async def on_message(self, message):
        # Jeśli wiadomość pochodzi od bota, ignorujemy ją
        if message.author == self.bot.user:
            return

        if not self.system_active.get(message.channel.id, False):
            await self.bot.process_commands(message)

        # Sprawdź, czy wiadomość jest komendą; jeśli tak, przekaż ją do systemu komend
        if message.content.startswith(self.bot.command_prefix):
            await self.bot.process_commands(message)
            return  # Wyjście z funkcji on_message, aby uniknąć dalszej logiki

        # Sprawdzanie, czy system jest aktywny na kanale
        if message.channel.id in self.active_systems:
            system_info = self.active_systems[message.channel.id]

            # System 2d20
            if system_info['system'] == '2d20' and system_info['end_time'] > datetime.datetime.utcnow():
                # Logika dla rzutów kostką
                k6_match = re.match(r'!(\d*)k6', message.content)
                k20_match = re.match(r'!(\d*)k20;(\d+)', message.content)

                if k6_match:
                    if message.channel.id not in self.system_active or not self.system_active[message.channel.id]:
                        embed = roll_k6(message.content, message.author.display_name)
                        await message.channel.send(embed=embed)
                        self.system_active[message.channel.id] = True
                    return  # Wyjście, aby uniknąć wysyłania wiadomości ponownie

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

            if system_info['end_time'] <= datetime.datetime.utcnow():
                if self.system_active.get(message.channel.id, False):
                    self.system_active[message.channel.id] = False

def setup(bot):
    bot.add_cog(MessageEvents(bot))
