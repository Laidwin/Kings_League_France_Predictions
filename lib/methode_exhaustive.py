from itertools import product


def methode_exhaustive(current_points: dict[str, int], remaining_matches: list[tuple[str, str]]) -> dict[str, list[int]]:
    """
    Simule les résultats des matchs restants en utilisant la méthode exhaustive.
    
    Args:
        current_points (dict[str, int]): Dictionnaire contenant les points actuels de chaque équipe.
        remaining_matches (list[tuple[str, str]]): Liste des matchs restants à jouer, chaque match étant représenté par un tuple d'équipes.

    Returns:
        dict[str, list[int]]: Dictionnaire contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Définition des équipes et issues possibles d’un match
    teams: list[str] = list(current_points.keys())
    match_outcomes: list[tuple[int, int]] = [(3, 0), (2, 1), (1, 2), (0, 3)]

    # Génération de toutes les combinaisons possibles de résultats
    total_scenarios: int = len(match_outcomes) ** len(remaining_matches)
    all_combinations: product[tuple[tuple[int, int], ...]] = product(match_outcomes, repeat=len(remaining_matches))

    # Compteur de positions finales pour chaque équipe
    position_counter: dict[str, list[int]] = {team: [0] * len(teams) for team in teams}

    # Simulation des scénarios
    outcome_set: tuple[tuple[int, int], ...]
    for outcome_set in all_combinations:
        points: dict[str, int] = current_points.copy()
        match: tuple[str, str]
        outcome: tuple[int, int]
        for match, outcome in zip(remaining_matches, outcome_set):
            team1: str
            team2: str
            team1, team2 = match
            pts1: int
            pts2: int
            pts1, pts2 = outcome
            points[team1] += pts1
            points[team2] += pts2

        # Tri des équipes par points
        sorted_teams: list[tuple[str, int]] = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        position: int
        team: str
        for position, (team, _) in enumerate(sorted_teams):
            position_counter[team][position] += 1

    return position_counter, total_scenarios