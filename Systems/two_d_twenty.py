import random
import re
from nextcord import Embed


# Funkcja do rzutu kostką k6
def roll_k6(message_content, display_name):
    # Sprawdzanie czy wiadomość pasuje do wzorca kostki k6
    k6_match = re.match(r'!(\d*)k6', message_content)

    # Słownik wyników dla kostki k6
    outcomes = {1: '1', 2: '2', 3: '0', 4: '0', 5: '1 (**Efekt**)', 6: '1 (**Efekt**)'}
    rolls = []
    total_points, effects = 0, 0

    # Ilość rzutu kostką
    num_dice = int(k6_match.groups()[0]) if k6_match.groups()[0] else 1

    # Rzuty kostką k6
    for _ in range(num_dice):
        roll = random.randint(1, 6)
        rolls.append(roll)
        if "Efekt" in outcomes[roll]:
            effects += 1
        total_points += int(outcomes[roll][0])

    # Sortowanie i przygotowanie listy wyników
    rolls.sort()
    results = [f"{roll} - {outcomes[roll]}" for roll in rolls]

    # Tworzenie i wysyłanie embeda
    embed = Embed(
        title=f"{display_name} rzuca kostką k6 {num_dice} razy",
        description='\n'.join(results),
        color=0x3498db
    )

    summary_text = f"Suma punktów: {total_points}\nIlość efektów: {effects}"

    embed.add_field(
        name="Podsumowanie",
        value=summary_text,
        inline=False
    )

    return embed


# Funkcja do rzutu kostką k20
def roll_k20(message_content, display_name):
    # Sprawdzanie czy wiadomość pasuje do wzorca kostki k20
    k20_match = re.match(r'!(\d*)k20;(\d+)', message_content)

    # Określa liczbę rzutów kostką i próg sukcesu
    num_dice = int(k20_match.groups()[0]) if k20_match.groups()[0] else 1
    threshold = int(k20_match.groups()[1])
    successes, crits, complications = 0, 0, 0
    rolls = []

    # Rzuty kostką k20
    for _ in range(num_dice):
        roll = random.randint(1, 20)
        rolls.append(roll)

        # Liczenie sukcesów, krytycznych sukcesów i komplikacji
        if roll == 1:
            successes += 2
            crits += 1
        elif roll == 20:
            complications += 1
        elif roll <= threshold:
            successes += 1

    # Sortowanie i przygotowanie listy wyników
    rolls.sort()
    results = []
    for i, roll in enumerate(rolls):
        results.append(
            f"{chr(65 + i)}. {roll} - {'Sukces (**Kryt**)' if roll == 1 else 'Porażka (**Komplikacja**)' if roll == 20 else 'Sukces' if roll <= threshold else 'Porażka'}"
        )

    # Tworzenie i wysyłanie embeda
    embed = Embed(
        title=f"{display_name} rzuca kostką k20 {num_dice} razy dla testu {threshold}",
        description='\n'.join(results),
        color=0x3498db
    )

    # Tworzenie i wysyłanie embeda
    summary_items = [("Ilość Sukcesów", successes)]
    if crits > 0:
        summary_items.append(("Ilość Krytów", crits))
    if complications > 0:
        summary_items.append(("Ilość Komplikacji", complications))

    summary_text = "\n".join([f"{name}: {value}" for name, value in summary_items])

    embed.add_field(
        name="Podsumowanie",
        value=summary_text,
        inline=False
    )

    return embed, num_dice


# Obsługa reakcji na wiadomość
async def handle_reaction_add_2d20(reaction, user, bot):
    if user == bot.user:
        return

    message = reaction.message

    # Pobranie nazwy użytkownika z tytułu embeda
    user_display_name = message.embeds[0].title.split()[0]

    # Jeśli użytkownik, który dodał reakcję, nie jest tym samym użytkownikiem, który wysłał oryginalną wiadomość
    if user_display_name != user.display_name:
        await reaction.remove(user)  # Usuń reakcję tego użytkownika
        return

    # Sprawdź, czy reakcja jest ":x:"
    if reaction.emoji == '❌' and message.author == bot.user:
        # Usuń wszystkie reakcje z wiadomości
        await reaction.message.clear_reactions()

    if reaction.emoji == '🔄' and message.author == bot.user:
        if 'k20' not in message.embeds[0].title:
            return

        reroll_indexes = []
        for i, react in enumerate(message.reactions[:-2]):  # -2 to exclude last two reactions 🔄 and ❌
            if user in await react.users().flatten():
                reroll_indexes.append(i)

        original_rolls = [int(re.search(r'\d+', res).group()) for res in message.embeds[0].description.split('\n')]
        threshold = int(re.search(r'(\d+)$', message.embeds[0].title).group())
        successes, crits, complications = 0, 0, 0

        rerolled_values = {}
        for i in reroll_indexes:
            new_roll = random.randint(1, 20)
            rerolled_values[i] = (original_rolls[i], new_roll)
            original_rolls[i] = new_roll

        original_rolls.sort()

        for roll in original_rolls:
            if roll == 1:
                successes += 2
                crits += 1
            elif roll == 20:
                complications += 1
            elif roll <= threshold:
                successes += 1

        await message.delete()

        results = []
        for index, roll in enumerate(original_rolls):
            prev_value = rerolled_values.get(index, (None, None))[0]

            if prev_value is not None:
                results.append(
                    f"{roll} (było {prev_value}) - {'Sukces (**Kryt**)' if roll == 1 else 'Porażka (**Komplikacja**)' if roll == 20 else 'Sukces' if roll <= threshold else 'Porażka'}"
                )
            else:
                results.append(
                    f"{roll} - {'Sukces (**Kryt**)' if roll == 1 else 'Porażka (**Komplikacja**)' if roll == 20 else 'Sukces' if roll <= threshold else 'Porażka'}"
                )

        # Utwórz i sformatuj embed z wynikami po przerzucie
        embed = Embed(
            title=f"{user.display_name} Twoje wyniki po przerzucie",
            description='\n'.join(results),
            color=0x3498db
        )

        summary_items = [("Ilość Sukcesów", successes)]
        if crits > 0:
            summary_items.append(("Ilość Krytów", crits))
        if complications > 0:
            summary_items.append(("Ilość Komplikacji", complications))

        summary_text = "\n".join([f"{name}: {value}" for name, value in summary_items])

        embed.add_field(
            name="Podsumowanie",
            value=summary_text,
            inline=False
        )

        await message.channel.send(embed=embed)