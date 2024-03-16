def get_help_message(bot_prefix):
    help_message = f"**{bot_prefix}help** - Wyświetla tę wiadomość z opisem wszystkich dostępnych komend.\n\n"
    help_message += f"**System 2d20 aktywny**:\n"
    help_message += f"**{bot_prefix}k6** - Rzut jedną lub więcej kostkami k6. Każda '1' to 1 punkt, '2' to 2 punkty, '3' i '4' to 0 punktów, '5' i '6' to 1 punkt oraz Efekt. Użycie: `{bot_prefix}Xk6`.\n\n"
    help_message += f"**{bot_prefix}k20** - Rzut jedną lub więcej kostkami k20, gdzie każdy wynik równy lub niższy od progu Y jest sukcesem. '1' to krytyczny sukces (2 sukcesy), '20' to komplikacja. Użycie: `{bot_prefix}Xk20;Y`.\n\n"
    help_message += "**System SWAE aktywny**:\n"
    help_message += f"**{bot_prefix}test** - Rzuty kostką typu Y z opcjonalnym modyfikatorem. Jeśli liczba rzutów (X) to 1, rzuca dodatkowo kością figury (k6) i zwraca lepszy wynik. Użycie: `{bot_prefix}test [X]kY[+Z/-Z]`.\n\n"
    help_message += f"**{bot_prefix}damage** - Rzuty kostkami określonymi przez Y oraz opcjonalne Z, suma wyników plus/minus modyfikator. Użycie: `{bot_prefix}damage Y[;Z][+A/-A]`.\n\n"

    # Tutaj dodajemy nową komendę rzutu, którą zdefiniowaliśmy
    help_message += "**Nowa komenda rzutu**:\n"
    help_message += f"**{bot_prefix}rzuc** - Wykonuje rzuty kostkami zgodnie z przekazanymi parametrami. Można definiować różne typy kostek, ich ilość oraz modyfikatory. Użycie: `{bot_prefix}rzuć [X]kY[+Z/-Z] [X]kY[+Z/-Z] ...`.\n\n"

    return help_message