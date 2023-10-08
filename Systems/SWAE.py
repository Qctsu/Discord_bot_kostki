import random
import re
from nextcord import Embed


# Funkcja do testów
async def test(message_content, display_name):
    test_match = re.match(r'!test (\d*)k(\d+)([+\-]\d+)?', message_content)

    if test_match is None:
        return None, False

    num_dice = int(test_match.groups()[0]) if test_match.groups()[0] else 1
    dice_type = int(test_match.groups()[1])
    modifier = int(test_match.groups()[2]) if test_match.groups()[2] else 0

    total_roll = 0
    all_rolls = []
    for _ in range(num_dice):
        roll = random.randint(1, dice_type)
        while roll == dice_type:
            roll += random.randint(1, dice_type)
        roll += modifier
        total_roll += roll
        all_rolls.append(roll)

    wild_roll = random.randint(1, 6)
    while wild_roll == 6:
        wild_roll += random.randint(1, 6)
    wild_roll += modifier

    highest_dice_roll = max(max(all_rolls), wild_roll)
    higher_roll = max(total_roll, wild_roll)

    outcome = ""
    can_reroll = True

    if any(roll == 1 for roll in all_rolls) and wild_roll == 1:
        outcome = "Krytyczny pech"
        can_reroll = False
    elif higher_roll < 4:
        outcome = "Porażka"
    elif 4 <= higher_roll < 8:
        outcome = "Sukces"
    elif higher_roll >= 8:
        outcome = "Przebicie"

    embed = Embed(
        title=f"{display_name} wykonuje test kością k{dice_type}",
        description=(
            f"Wyniki Kostek: {', '.join([str(roll) for roll in all_rolls])}\n"
            f"Wynik Kości Figury: {wild_roll}\n\n"
            f"Najwyższy rzut: **{highest_dice_roll}**\n"
            f"Wynik: **{outcome}**"
        ),
        color=0x3498db
    )

    return embed, can_reroll


async def damage(message_content, display_name):
    # Wzorzec do dopasowania komendy !damage
    damage_match = re.match(r'!damage (?:k)?(\d+)(?:;(?:k)?(\d+))*(?:([+\-]\d+))?', message_content)

    # Jeśli wzorzec nie pasuje, zwracamy None
    if damage_match is None:
        return None

    # Grupy dopasowania
    dice_values = re.findall(r'\d+', damage_match.group(0))  # Znajduje wszystkie wartości rzutów kostką
    modifier = damage_match.groups()[-1] if damage_match.groups()[-1] is not None else "+0"  # Znajduje modyfikator

    # Dzieli modyfikator na znak i wartość
    modifier_sign = "+" if modifier[0] == '+' else "-"
    modifier_value = int(modifier[1:]) if len(modifier) > 1 else 0

    rolls = []

    # Dla każdej wartości kostki wykonuje rzut i dodaje do listy rzutów
    for dice in dice_values:
        dice_type = int(dice)
        roll = random.randint(1, dice_type)
        rolls.append(roll)

    # Oblicza całkowite obrażenia
    total_damage = sum(rolls)
    # Dodanie lub odjęcie wartości modyfikatora
    if modifier_sign == '+':
        total_damage += modifier_value
    elif modifier_sign == '-':
        total_damage -= modifier_value

    # Tworzenie tytułu zawierającego informacje o rodzaju kostek i modyfikatorze
    dice_types = [f"k{dice}" for dice in dice_values[:-1]]  # Wyklucz ostatni element (modyfikator)
    title = f"{display_name} rzuca obrażenia kostką: {', '.join(dice_types)} z modyfikatorem {modifier_sign}{modifier_value}"

    # Usuwanie niepotrzebnego 'k' przed liczbami kostek
    title = re.sub(r'k0*(\d+)', r'k\1', title)

    # Tworzenie embeda z tytułem i osobnym opisem dla sumy wyników
    embed = Embed(
        title=title,
        description=f"Wynik kostek: {total_damage}",
        color=0x3498db
    )

    return embed


async def handle_reaction_add_SWAE(reaction, user, bot, user_last_commands):
    if user == bot.user:
        return

    message = reaction.message

    # Sprawdź, czy reakcja jest ":x:"
    if reaction.emoji == '❌' and message.author == bot.user:
        # Usuń wszystkie reakcje z wiadomości
        await reaction.message.clear_reactions()

    # Sprawdzanie czy reakcja jest ":arrows_counterclockwise:" i czy wiadomość zawiera "!test"
    elif reaction.emoji == '🔄' and message.author == bot.user:
        if message.id in user_last_commands:
            user_id = user_last_commands[message.id]["user_id"]  # Pobierz nazwę użytkownika po ID wiadomości
            command = user_last_commands[message.id]["command"]

            # Wykonaj przerzut używając komendy zapisanej w user_last_commands
            result = await test(command, user_id)

            if result:
                embed, can_reroll = result

                # Zachowaj oryginalny embed
                original_embed = message.embeds[0]

                # pobieranie opisu nowego embeda
                new_embed = embed.copy()
                additional_description = new_embed.description

                # Dodaj dodatkowy opis na końcu opisu oryginalnego embeda
                original_embed.description += f"\n\n**Wyniki po przerzucie**\n{additional_description}"

                # Zaktualizuj wiadomość z wynikiem przerzutu
                await message.edit(embed=original_embed)

                # Usuń reakcję po przerzucie
                await reaction.message.clear_reactions()
