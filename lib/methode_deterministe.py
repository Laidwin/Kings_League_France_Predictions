import random


def methode_deterministe(num_simulations:int, current_points: dict[str, int], remaining_matches: list[tuple[str, str]]) -> dict[str, list[int]]:
    """
    Simule les résultats des matchs restants en utilisant la méthode déterministe.

    Args:
        num_simulations (int): Nombre de simulations à effectuer.
        current_points (dict[str, int]): Dictionnaire contenant les points actuels des équipes.

    Returns:
        dict[str, list[int]]: Dictionnaire contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Définition des équipes et issues possibles d’un match
    teams: list[str] = list(current_points.keys())
    match_outcomes: list[tuple[int, int]] = [(3, 0), (2, 1), (1, 2), (0, 3)]

    # Génération aléatoire de num_simulations combinaisons de résultats
    random_combinations: list[tuple[tuple[int, int], ...]] = [
        tuple(random.choices(match_outcomes, k=len(remaining_matches)))
        for _ in range(num_simulations)
    ]

    # Compteur de positions finales pour chaque équipe
    position_counter: dict[str, list[int]] = {team: [0] * len(teams) for team in teams}

    # Simulation des scénarios
    outcome_set: tuple[tuple[int, int], ...]
    for outcome_set in random_combinations:
        points:dict[str, int] = current_points.copy()
        match:tuple[str, str]
        outcome:tuple[int, int]
        for match, outcome in zip(remaining_matches, outcome_set):
            team1:str
            team2
            team1, team2 = match
            pts1:int
            pts2:int
            pts1, pts2 = outcome
            points[team1] += pts1
            points[team2] += pts2

        # Tri des équipes par points
        sorted_teams: list[tuple[str, int]] = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        position:int
        team:str
        for position, (team, _) in enumerate(sorted_teams):
            position_counter[team][position] += 1
    return position_counter