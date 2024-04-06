import numpy as np  # Importuj bibliotekę numpy do generowania losowych liczb
import nextcord  # Importuj bibliotekę nextcord do tworzenia embedów dla Discorda
import re  # Importuj moduł wyrażeń regularnych do analizowania notacji kości

def roll_dice(dice_notation: str):
    # Funkcja do obliczania wyniku rzutu kośćmi na podstawie podanej notacji

    def single_roll(rolls, sides):
        # Generuje losowe wyniki dla zadanej liczby rzutów kością o określonej liczbie ścian
        return np.random.randint(1, sides + 1, rolls)

    def parse_expression(expression):
        # Analizuje wyrażenie rzutu kośćmi, włączając modyfikatory i stałe wartości
        matches = re.findall(r'([+-]?)\s*(\d*)[dDkK](\d+)|([+-]\d+)', expression)
        details = []

        for sign, num_rolls, sides, constant in matches:
            if constant:  # Obsługa stałych wartości jako modyfikatorów
                details.append((sign, 0, 0, [], int(constant)))
            else:  # Obsługa rzutów kośćmi
                rolls = int(num_rolls) if num_rolls else 1  # Domyślnie jeden rzut, jeśli liczba nie jest określona
                dice_results = single_roll(rolls, int(sides))  # Wyniki pojedynczych rzutów
                sum_of_dice = np.sum(dice_results)  # Suma wyników rzutów
                details.append((sign, rolls, sides, dice_results, sum_of_dice))

        return details

    expressions = dice_notation.split()  # Rozdziel notację na poszczególne wyrażenia
    total_sum = 0  # Suma wszystkich rzutów i modyfikatorów
    detailed_results = []  # Szczegółowe wyniki do wyświetlenia

    for expression in expressions:
        parts = re.split(r'(?=[+-])', expression)  # Podziel wyrażenie na części z modyfikatorami
        expr_details = []  # Szczegóły dla tego wyrażenia
        expr_sum = 0  # Suma dla tego wyrażenia
        mod_sum = 0  # Suma modyfikatorów
        mod_details = []  # Szczegółowe informacje o modyfikatorach

        for part in parts:
            for sign, rolls, sides, dice_results, value in parse_expression(part.strip()):
                if sign:
                    # Obsługa modyfikatorów i stałych wartości
                    mod_sum += value if sign == '+' else -value
                    if rolls:  # Formatowanie wyników rzutów kośćmi z modyfikatorami
                        # mod_details.append(f"{sign}{rolls}d{sides}: {', '.join(map(str, dice_results))} => Suma: {value if sign == '+' else -value}")
                        mod_details.append(f"{sign}{rolls}d{sides}: {', '.join(map(str, dice_results))} => Suma: {value if sign == '+' else -value}")
                    else:  # Formatowanie stałych wartości jako modyfikatorów
                        mod_details.append(f"{sign}{value}")
                else:
                    # Główny rzut bez modyfikatorów
                    expr_sum += value
                    if rolls:
                        expr_details.append(f"{rolls}d{sides}: {', '.join(map(str, dice_results))}")

        final_sum = expr_sum + mod_sum  # Suma wyników i modyfikatorów dla tego wyrażenia
        total_sum += final_sum  # Dodaj do łącznej sumy
        if value != expr_sum:
            mod_str = f" (modyfikator: {value})"
        else:
            mod_str = f" (modyfikator: {', '.join(mod_details)})" if mod_details else ""  # Formatowanie modyfikatorów do wyświetlenia
        detailed_results.append(f"{', '.join(expr_details)} => Suma: {final_sum}{mod_str}")

    return total_sum, detailed_results  # Zwraca łączną sumę i szczegółowe wyniki

# def generate_embed(dice_expression: str, author: str):
#     # Tworzy embed z wynikami rzutów kośćmi dla autora
#     total_sum, results = roll_dice(dice_expression)  # Oblicz wyniki rzutów na podstawie notacji
#     embed = nextcord.Embed(title=f"{author} - wyniki rzutów", description="", color=0x00ff00)  # Utwórz embed z podstawowymi informacjami
#     for result in results:
#         embed.add_field(name="Rzut", value=result, inline=False)  # Dodaj pola dla każdego rzutu
#     embed.add_field(name="Łączna suma punktów", value=str(total_sum), inline=False)  # Dodaj pole z łączną sumą punktów
#     return embed  # Zwróć gotowy embed
#
# # Zmodyfikowana wersja funkcji generate_embed, aby działała w środowisku bez nextcord
# def generate_embed(dice_expression: str, author: str):
#     total_sum, results = roll_dice(dice_expression)
#     print(f"{author} - wyniki rzutów")  # Wyświetlamy tytuł
#     for result in results:
#         print(f"Rzut: {result}")  # Wyświetlamy wyniki poszczególnych rzutów
#     print(f"Łączna suma punktów: {total_sum}")  # Wyświetlamy łączną sumę punktów
#
# # Przykładowe wywołanie
# dice_expression = "2d20-4d10 3k6+d2 k12+1 3d6"
# author = "Gracz1"
# generate_embed(dice_expression, author)
