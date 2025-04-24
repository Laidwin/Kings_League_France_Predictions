import random

def monte_carlo(nb_sim: int, teams: dict[str, int], remaining_matches: list[tuple[str, str]]) -> dict[str, list[int]]:
    """
    Simule les résultats des matchs restants en utilisant la méthode de Monte Carlo.

    Args:
        nb_sim (int): Nombre de simulations à effectuer.
        teams (dict[str, int]): Dictionnaire contenant les équipes et leurs points actuels.
        remaining_matches (list[tuple[str, str]]): Liste des matchs restants à simuler.

    Returns:
        dict[str, list[int]]: Dictionnaire contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Compteur de positions
    position_counter: dict[str, list[int]] = {team: [0] * len(teams) for team in teams}

    # Simulation des résultats
    for _ in range(nb_sim):
        points: dict[str, int] = teams.copy()
        match: tuple[str, str]
        for match in remaining_matches:
            result: str = random.choices(
                population=["win1", "draw_win1", "draw_win2", "win2"],
            )[0]

            if result == "win1":
                points[match[0]] += 3
            elif result == "win2":
                points[match[1]] += 3
            elif result == "draw_win1":
                points[match[0]] += 2
                points[match[1]] += 1
            elif result == "draw_win2":
                points[match[0]] += 1
                points[match[1]] += 2

        # Classer les équipes
        sorted_teams: list[tuple[str, int]] = sorted(points.items(), key=lambda x: (-x[1], x[0]))

        # Mettre à jour les stats de position
        pos: int
        team: str
        for pos, (team, _) in enumerate(sorted_teams):
            position_counter[team][pos] += 1

    return position_counter