"""Simulation exhaustive de tous les scénarios possibles."""

from concurrent.futures import ProcessPoolExecutor
from itertools import islice, product
from os import cpu_count

# Issues possibles d'un match : victoire (3 pts) ou défaite (0 pts), pas de nul
MATCH_OUTCOMES: list[tuple[int, int]] = [(3, 0), (0, 3)]


def simulate_exhaustive(
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
) -> tuple[dict[str, list[int]], int]:
    """Énumère tous les scénarios possibles et calcule les classements."""
    teams = list(standings.keys())
    nb_teams = len(teams)
    nb_matches = len(remaining_matches)
    total_scenarios = len(MATCH_OUTCOMES) ** nb_matches

    position_counter: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}

    for outcome_set in product(MATCH_OUTCOMES, repeat=nb_matches):
        points = standings.copy()
        for (home, away), (pts_h, pts_a) in zip(remaining_matches, outcome_set, strict=True):
            points[home] += pts_h
            points[away] += pts_a

        sorted_teams = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        for pos, (team, _) in enumerate(sorted_teams):
            position_counter[team][pos] += 1

    return position_counter, total_scenarios


# --- Version multiprocessing ---


def _simulate_chunk(
    start: int,
    size: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
    teams: list[str],
) -> dict[str, list[int]]:
    """Simule un sous-ensemble de scénarios dans un processus séparé."""
    nb_teams = len(teams)
    nb_matches = len(remaining_matches)
    counter: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}

    scenarios = islice(
        product(range(len(MATCH_OUTCOMES)), repeat=nb_matches),
        start,
        start + size,
    )

    for outcome_indices in scenarios:
        points = standings.copy()
        for (home, away), idx in zip(remaining_matches, outcome_indices, strict=True):
            pts_h, pts_a = MATCH_OUTCOMES[idx]
            points[home] += pts_h
            points[away] += pts_a

        sorted_teams = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        for pos, (team, _) in enumerate(sorted_teams):
            counter[team][pos] += 1

    return counter


def simulate_exhaustive_mp(
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
) -> tuple[dict[str, list[int]], int]:
    """Version multiprocessing de la simulation exhaustive."""
    teams = list(standings.keys())
    nb_teams = len(teams)
    nb_matches = len(remaining_matches)
    total_scenarios = len(MATCH_OUTCOMES) ** nb_matches

    num_workers = cpu_count() or 4
    chunk_size = total_scenarios // num_workers
    remainder = total_scenarios % num_workers

    chunks = []
    offset = 0
    for i in range(num_workers):
        size = chunk_size + (1 if i < remainder else 0)
        chunks.append((offset, size))
        offset += size

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(_simulate_chunk, start, size, standings, remaining_matches, teams) for start, size in chunks
        ]
        results = [f.result() for f in futures]

    merged: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}
    for result in results:
        for team in teams:
            for pos in range(nb_teams):
                merged[team][pos] += result[team][pos]

    return merged, total_scenarios
