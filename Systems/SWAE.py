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

    all_rolls = []
    for _ in range(num_dice):
        roll = 0  # Resetujemy wartość roll przy każdej nowej kostce
        current_roll = random.randint(1, dice_type)  # Pierwszy rzut kostką
        explosions = 0  # Resetujemy licznik eksplozji

        while current_roll == dice_type and explosions < 10:  # Sprawdzamy eksplozje
            roll += current_roll  # Dodajemy aktualny rzut do sumy
            current_roll = random.randint(1, dice_type)  # Rzucamy jeszcze raz
            explosions += 1  # Zwiększamy licznik eksplozji

        roll += current_roll + modifier  # Dodajemy ostatni rzut i modyfikator do sumy
        all_rolls.append(roll)  # Dodajemy sumę do listy

    wild_roll = random.randint(1, 6)
    explosions = 0

    while wild_roll == 6 and explosions < 10:
        wild_roll += random.randint(1, 6)
        explosions += 1

    wild_roll += modifier

    highest_dice_roll = max(all_rolls)
    highest_roll = max(highest_dice_roll, wild_roll)

    outcome = ""
    can_reroll = True

    if any(roll == 1 for roll in all_rolls) and wild_roll == 1:
        outcome = "Krytyczny pech"
        can_reroll = False
    elif highest_roll < 4:
        outcome = "Porażka"
    elif 4 <= highest_roll < 8:
        outcome = "Sukces"
    elif highest_roll >= 8:
        outcome = "Przebicie"

    if modifier>0:
        title = f"{display_name} wykonuje test kością k{dice_type} z modyfikatorem +{modifier}"
    elif modifier!=0:
        title = f"{display_name} wykonuje test kością k{dice_type} z modyfikatorem {modifier}"
    else:
        title = f"{display_name} wykonuje test kością k{dice_type}"

    embed = Embed(
        title=title,
        description=(
            f"Wyniki Kostek: {', '.join([str(roll) for roll in all_rolls])}\n"
            f"Wynik Kości Figury: {wild_roll}\n\n"
            f"Najwyższy rzut: **{highest_roll}**\n"
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

    # Wyszukuje dopasowania
    damage_match = re.search(r'(\d+(?:;\d+)*)([-+]\d+)?$', damage_match.group(0))

    if damage_match:
        # Grupy dopasowania
        dice_values = [int(value) for value in re.findall(r'\d+', damage_match.group(1))]  # Znajduje wszystkie wartości rzutów kostką
        modifier = damage_match.group(2) if damage_match.group(2) is not None else "+0"  # Znajduje modyfikator

        # Dzieli modyfikator na znak i wartość
        modifier_sign = "+" if modifier[0] == '+' else "-"
        modifier_value = int(modifier[1:]) if len(modifier) > 1 else 0

        rolls = []
        all_rolls = []

    for dice in dice_values:
        print(f"kostka którą rzucamy: {dice}")
        roll =0 # Resetujemy wartość roll przy każdej nowej kostce
        current_roll = random.randint(1, int(dice)) # pierwszy rzut kością
        explosions = 0 #resetujemy eksplozje
        print(f"Rzut kością: {current_roll}")

        while current_roll == dice and explosions < 10: # Sprawdzamy eksplozje
            print(f"Eksplozja!")
            roll += current_roll # Dodajemy aktualny rzut do sumy
            print(F"Wartość roll: {roll}")
            current_roll = random.randint(1, int(dice))  # Rzucamy jeszcze raz
            print(f"Rzut kością po eksplozji: {current_roll}")
            explosions += 1  # Zwiększamy licznik eksplozji

        roll += current_roll  # Dodajemy ostatni rzut i modyfikator do sumy
        all_rolls.append(roll)  # Dodajemy sumę do listy

    # Oblicza całkowite obrażenia
    total_damage = sum(all_rolls)
    # Dodanie lub odjęcie wartości modyfikatora
    if modifier_sign == '+':
        total_damage += modifier_value
    elif modifier_sign == '-':
        total_damage -= modifier_value
    print(f"-------------")

    # Tworzenie tytułu zawierającego informacje o rodzaju kostek i modyfikatorze
    dice_types = [f"k{dice}" for dice in dice_values]
    if modifier_value>0:
        title = f"{display_name} rzuca obrażenia kostką: {', '.join(dice_types)} z modyfikatorem {modifier_sign}{modifier_value}"
    else:
        title = f"{display_name} rzuca obrażenia kostką: {', '.join(dice_types)}"

    # Print each roll result
    for i, roll in enumerate(rolls):
        print(f"Rzut {i + 1}: {roll}")

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
