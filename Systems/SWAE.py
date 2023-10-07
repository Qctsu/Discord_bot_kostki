import random
import re
from nextcord import Embed

# Funkcja do testów
async def test(message_content, display_name):
    # Sprawdzanie czy wiadomość pasuje do wzorca rzutu
    test_match = re.match(r'!test (\d*)k(\d+)([+\-]\d+)?', message_content)

    # Brak dopasowania - nie jest to prawidłowy rzut
    if test_match is None:
        return None

    # Określa liczbę rzutów kostką, rodzaj kości i modyfikator
    num_dice = int(test_match.groups()[0]) if test_match.groups()[0] else 1
    dice_type = int(test_match.groups()[1])
    modifier = int(test_match.groups()[2]) if test_match.groups()[2] else 0

    # Rzuty kostką i kością figury
    total_roll = 0
    all_rolls = []
    for _ in range(num_dice):
        roll = random.randint(1, dice_type)
        while roll == dice_type:  # Exploding dice
            roll += random.randint(1, dice_type)
        roll += modifier  # Dodawanie modyfikatora do rzutu
        total_roll += roll
        all_rolls.append(roll)

    wild_roll = 0
    # Rzut kością figury (k6) z modyfikatorem
    wild_roll = random.randint(1, 6)
    while wild_roll == 6:  # Exploding dice
        wild_roll += random.randint(1, 6)
    wild_roll += modifier  # Dodawanie modyfikatora do rzutu kością figury

    # Dodawanie rzutu kością figury do sumy wszystkich rzutów
    total_roll += wild_roll

    # Tworzenie embeda
    embed = Embed(
        title=f"{display_name} wykonuje test kością k{dice_type}",
        description=f"Wyniki Kostek: {', '.join([str(roll) for roll in all_rolls])}\nWynik Kości Figury: {wild_roll}",
        color=0x3498db
    )

    return embed


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