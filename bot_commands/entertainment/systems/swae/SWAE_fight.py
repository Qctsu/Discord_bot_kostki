from nextcord.ext import commands
from nextcord import Embed, Member, Reaction
import config.db_config as db_config
import aiosqlite
import random

NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
CHECK_EMOJI = "✅"

SUITS = ['Kier', 'Karo', 'Trefl', 'Pik']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Walet', 'Królowa', 'Król', 'As']
DECK = [(rank, suit) for suit in SUITS for rank in RANKS] + [('Joker', 'Czerwony'), ('Joker', 'Czarny')]


async def show_initiative_results(channel, sorted_cards):
    # Tworzenie embedu z wynikami inicjatywy
    embed = Embed(title="Wyniki inicjatywy:", color=0x3498db)

    for index, (participant, card) in enumerate(sorted_cards, start=1):
        embed.add_field(name=f"{index}. {participant}", value=f"{card[0]} {card[1]}", inline=False)

    await channel.send(embed=embed)


class Combat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_combats = {}
        self.selected_players_for_channel = {}
        self.combat_used_cards = {}
        self.DECK = [(rank, suit) for suit in SUITS for rank in RANKS] + [('Joker', 'Czerwony'), ('Joker', 'Czarny')]

    async def draw_initiative(self, ctx, num_enemies):
        players = self.selected_players_for_channel.get(ctx.channel.id)
        if not players:
            await ctx.send("Brak graczy w tej sesji.")
            return

        selected_names = [player[1] for player in players]

        num_players = len(players)
        if num_enemies <= 0:
            await ctx.send("Liczba wrogów musi być większa od zera.")
            return

        all_combatants = selected_names + [f"Wróg {i + 1}" for i in range(num_enemies)]

        if ctx.channel.id not in self.combat_used_cards:
            self.combat_used_cards[ctx.channel.id] = set()

        # Losowanie kart inicjatywy
        cards = [(combatant, self.draw_card(self.DECK, self.combat_used_cards, ctx.channel.id)) for combatant in all_combatants]
        sorted_cards = sort_cards(cards)

        # Sprawdź, czy wśród wylosowanych kart jest Joker
        joker_drawn = any(card[1][0] == 'Joker' for card in cards)

        # Jeśli Joker został wylosowany, przetasuj talie i wyświetl odpowiednią wiadomość
        if joker_drawn:
            self.combat_used_cards[ctx.channel.id].clear()
            random.shuffle(self.DECK)
            await ctx.send("Joker został wylosowany. Talia została przetasowana.")

        if num_enemies > 0:
            # Pokaż embed z wynikami tylko wtedy, gdy jest przynajmniej 1 wróg
            await show_initiative_results(ctx.channel, sorted_cards)

    def draw_card(self, deck, used_cards, channel_id):
        available_cards = [card for card in deck if card not in used_cards[channel_id]]
        if not available_cards:
            used_cards[channel_id].clear()
            available_cards = deck
        card = random.choice(available_cards)
        used_cards[channel_id].add(card)
        return card


    @commands.command(name="walka")
    async def walka(self, ctx, *, subcommand: str):
        if subcommand.lower() == "start":
            await self.start_combat(ctx)
        elif subcommand.isdigit():
            num_enemies = int(subcommand)
            if num_enemies > 0:
                await self.draw_initiative(ctx, num_enemies)
            else:
                await ctx.send("Liczba wrogów musi być większa od zera.")
        elif subcommand.lower() == "koniec":
            await self.end_combat(ctx)  # Dodana komenda !walka koniec
        else:
            await ctx.send(
                "Niewłaściwe użycie komendy `!walka`. Użyj `!walka start`, `!walka <liczba_wrogów>` lub `!walka "
                "koniec`.")

    async def end_combat(self, ctx):
        # Resetuj używane karty i usuń informacje o wybranej sesji
        self.used_cards.clear()
        self.selected_players_for_channel.pop(ctx.channel.id, None)
        self.combat_used_cards.pop(ctx.channel.id, set())
        await ctx.send("Walka zakończona. Karty zostały przetasowane.")

    async def start_combat(self, ctx):
        gm_id = await get_gm_id_for_active_system(ctx.channel.id)

        if not gm_id:
            await ctx.send("Nie mogę znaleźć GM dla tego kanału.")
            return

        if str(ctx.author.id) != gm_id:
            await ctx.send("Tylko GM może rozpocząć walkę.")
            return

        players = await get_players_for_active_system(ctx.channel.id)
        if not players:
            await ctx.send("Brak graczy w tej sesji.")
            return

        description = "\n".join([f"{NUMBER_EMOJIS[index]} {player[1]}" for index, player in enumerate(players)])
        embed = Embed(title="Wybierz graczy do walki:", description=description, color=0x3498db)

        message = await ctx.send(embed=embed)
        for i in range(len(players)):
            await message.add_reaction(NUMBER_EMOJIS[i])
        await message.add_reaction(CHECK_EMOJI)
        self.active_combats[message.id] = players

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if reaction.message.id not in self.active_combats:
            return
        gm_id = await get_gm_id_for_active_system(reaction.message.channel.id)
        if not gm_id or str(user.id) != gm_id:
            return

        if str(reaction.emoji) == CHECK_EMOJI:
            all_reactions = reaction.message.reactions
            selected_indices = [NUMBER_EMOJIS.index(str(r.emoji)) for r in all_reactions if
                                str(r.emoji) in NUMBER_EMOJIS and user in await r.users().flatten()]

            # Wybór graczy
            selected_players = [self.active_combats[reaction.message.id][i] for i in selected_indices]
            self.selected_players_for_channel[reaction.message.channel.id] = selected_players  # Zapisujemy graczy
            await reaction.message.delete()
            del self.active_combats[reaction.message.id]

            # Tworzenie embedu z informacją o uczestniczących graczach
            players_info = "\n".join([f"{player[1]}" for player in selected_players])
            embed = Embed(title="Gracze uczestniczący w walce:", description=players_info, color=0x3498db)
            await reaction.message.channel.send(embed=embed)


async def get_gm_id_for_active_system(channel_id):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()
        sql = '''SELECT gm_id 
                 FROM game_sessions 
                 WHERE channel_id = ?'''
        await cursor.execute(sql, (channel_id,))
        result = await cursor.fetchone()
        return result[0] if result else None


async def get_players_for_active_system(channel_id):
    async with aiosqlite.connect(db_config.get_database_path()) as db:
        cursor = await db.cursor()
        sql = '''SELECT player_id, player_nick 
                 FROM session_players 
                 WHERE session_id = (SELECT session_id 
                                     FROM game_sessions 
                                     WHERE channel_id = ?)'''
        await cursor.execute(sql, (channel_id,))
        result = await cursor.fetchall()
        return result if result else []


def sort_cards(cards):
    def card_value(card_tuple):
        card = card_tuple[1]
        rank_index = RANKS.index(card[0]) if card[0] in RANKS else len(RANKS)
        # Definiowanie kolejności kolorów według zasad
        suit_order = {'Pik': 0, 'Kier': 1, 'Karo': 2, 'Trefl': 3}
        suit_index = suit_order.get(card[1], len(suit_order))
        return rank_index, suit_index

    return sorted(cards, key=card_value, reverse=True)
