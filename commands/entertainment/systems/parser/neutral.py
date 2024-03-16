import random
import re
from nextcord import Embed

def parse_dice_command(command):
    """
    Parsuje komendę zawierającą rzuty kostkami.
    Przykładowa komenda: "2k6+2 3k100+10 5k10-2"
    Obsługuje także przypadki bez wyraźnie podanej ilości rzutów, np. "k10+1".
    """
    dice_pattern = re.compile(r'(?:(\d+))?k(\d+)([+-]\d+)?')
    matches = dice_pattern.findall(command)
    parsed_commands = []
    for match in matches:
        num_rolls, dice_sides, modifier = match
        num_rolls = int(num_rolls) if num_rolls else 1  # Domyślnie 1 rzut, jeśli ilość nie jest podana
        dice_sides = int(dice_sides)
        modifier = int(modifier) if modifier else 0
        parsed_commands.append((num_rolls, dice_sides, modifier))
    return parsed_commands

def roll_dice(dice_commands, display_name):
    """
    Realizuje rzuty kostkami zgodnie z przekazanymi komendami.
    Zapewnia, że minimalny wynik rzutu (po dodaniu lub odjęciu modyfikatora) to 1.
    """
    results = []
    total_sum = 0

    for command in dice_commands:
        num_rolls, dice_sides, modifier = command
        rolls = []
        for _ in range(num_rolls):
            roll = random.randint(1, dice_sides) + modifier
            # Zapewniamy, że minimalny wynik to 1
            roll = max(roll, 1)
            rolls.append(roll)

        sum_rolls = sum(rolls)
        total_sum += sum_rolls

        # Przygotowanie opisu rzutów
        if modifier != 0:
            modifier_str = f"{modifier:+d}"
        else:
            modifier_str = ""
        rolls_str = ", ".join(map(str, rolls))
        results.append(f"{num_rolls}k{dice_sides}{modifier_str}: {rolls_str} => Suma: {sum_rolls}")

    # Tworzenie embeda
    embed = Embed(
        title=f"{display_name} - wyniki rzutów",
        description="\n".join(results),
        color=0x3498db
    )
    embed.add_field(
        name="Łączna suma punktów",
        value=str(total_sum),
        inline=False
    )

    return embed

# # Przykład użycia
# message_content = "!2k6+2 3k100+10 5k10-2"
# display_name = "Gracz"
#
# # Parsowanie komendy i rzuty kostkami
# dice_commands = parse_dice_command(message_content[1:])  # Usuwamy wykrzyknik z komendy
# embed = roll_dice(dice_commands, display_name)
#
# # embed można teraz wysłać jako wiadomość na serwerze Discord
