import numpy as np  # Importuj bibliotekę numpy do generowania losowych liczb
import nextcord  # Importuj bibliotekę nextcord do tworzenia embedów dla Discorda
import re  # Importuj moduł wyrażeń regularnych do analizowania notacji kości

def roll_dice(dice_notation: str):
    def single_roll(rolls, sides):
        return np.random.randint(1, sides + 1, rolls)

    def parse_expression(expression):
        # Zmodyfikowane, aby lepiej obsłużyć różne typy modyfikatorów
        matches = re.findall(r'([+-]?)\s*(\d*)[dDkK](\d+)|([+-]\d+)', expression)
        details = []

        for sign, num_rolls, sides, constant in matches:
            if constant:  # Obsługa stałych wartości
                value = int(constant)
                details.append((sign, 0, 0, [], value, 'constant'))
            else:
                rolls = int(num_rolls) if num_rolls else 1
                dice_results = single_roll(rolls, int(sides))
                sum_of_dice = np.sum(dice_results)
                details.append((sign, rolls, sides, dice_results, sum_of_dice, 'dice'))

        return details

    expressions = dice_notation.split()
    total_sum = 0
    detailed_results = []

    for expression in expressions:
        parts = re.split(r'(?=[+-])', expression)
        expr_details = []
        expr_sum = 0
        mod_sum = 0
        mod_details = []

        for part in parts:
            for sign, rolls, sides, dice_results, value, type in parse_expression(part.strip()):
                if sign:
                    # Modyfikatory, zarówno stałe wartości jak i rzuty
                    mod_sum += value if sign == '+' else -value
                    if type == 'dice':
                        mod_details.append(f"{sign}{rolls}k{sides}: {', '.join(map(str, dice_results))} => Suma: {sign}{value}")
                    else:  # Stałe wartości
                        mod_details.append(f"{sign}{value}")
                else:
                    # Główny rzut
                    expr_sum += value
                    if type == 'dice':
                        expr_details.append(f"{rolls}k{sides}: {', '.join(map(str, dice_results))}")

        final_sum = expr_sum + mod_sum
        total_sum += final_sum
        if sides==0:
            mod_str = f" (modyfikator: {part})"
        else:
            mod_str = f" (modyfikator: {' '.join(mod_details)})" if mod_details else ""
        detailed_results.append(f"{' '.join(expr_details)} => Suma: {final_sum}{mod_str}")

    return total_sum, detailed_results

def generate_embed(dice_expression: str, author: str):
    total_sum, results = roll_dice(dice_expression)
    embed = nextcord.Embed(title=f"{author} - wyniki rzutów", description="", color=0x00ff00)
    for result in results:
        embed.add_field(name="Rzut", value=result, inline=False)
    embed.add_field(name="Łączna suma punktów", value=str(total_sum), inline=False)
    return embed

# Zmodyfikowana wersja funkcji generate_embed, aby działała w środowisku bez nextcord
# def generate_embed(dice_expression: str, author: str):
#     total_sum, results = roll_dice(dice_expression)
#     print(f"{author} - wyniki rzutów")  # Wyświetlamy tytuł
#     for result in results:
#         print(f"Rzut: {result}")  # Wyświetlamy wyniki poszczególnych rzutów
#     print(f"Łączna suma punktów: {total_sum}")  # Wyświetlamy łączną sumę punktów
#
# # Przykładowe wywołanie
# dice_expression = "k12+1"
# author = "Gracz1"
# generate_embed(dice_expression, author)
