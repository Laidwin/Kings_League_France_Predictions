"""Simulation déterministe par tirage aléatoire de résultats discrets."""

import random

# Issues possibles d'un match : victoire (3 pts) ou défaite (0 pts), pas de nul
MATCH_OUTCOMES: list[tuple[int, int]] = [(3, 0), (0, 3)]


def simulate_deterministic(
    nb_simulations: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
) -> dict[str, list[int]]:
    """Simule les classements en tirant aléatoirement des résultats discrets.

    Chaque match peut se terminer par une victoire (3-0), un nul avantage
    domicile (2-1), un nul avantage extérieur (1-2) ou une défaite (0-3).
    """
    teams = list(standings.keys())
    nb_teams = len(teams)
    position_counter: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}

    for _ in range(nb_simulations):
        points = standings.copy()
        outcomes = random.choices(MATCH_OUTCOMES, k=len(remaining_matches))

        for (home, away), (pts_h, pts_a) in zip(remaining_matches, outcomes, strict=True):
            points[home] += pts_h
            points[away] += pts_a

        sorted_teams = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        for pos, (team, _) in enumerate(sorted_teams):
            position_counter[team][pos] += 1

    return position_counter
