"""Simulation Monte Carlo avec scores Poisson et classement vectorisé."""

from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from os import cpu_count

import numpy as np


def _compute_match_lambdas(
    remaining_matches: list[tuple[str, str]],
    strengths: dict[str, int],
    avg_goals: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Pré-calcule les paramètres lambda Poisson pour chaque match."""
    lambdas_a = []
    lambdas_b = []
    for home, away in remaining_matches:
        diff = (strengths[home] - strengths[away]) / 50
        lambdas_a.append(avg_goals * (1.35**diff))
        lambdas_b.append(avg_goals * (1.35 ** (-diff)))
    return np.array(lambdas_a), np.array(lambdas_b)


def _run_simulation(
    nb_sim: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
    strengths: dict[str, int],
    avg_goals: float,
    rng: np.random.Generator,
) -> dict[str, list[int]]:
    """Logique de simulation partagée entre les versions single et multiprocessing."""
    teams = list(standings.keys())
    nb_teams = len(teams)
    nb_matches = len(remaining_matches)
    team_idx = {team: i for i, team in enumerate(teams)}

    lambdas_a, lambdas_b = _compute_match_lambdas(remaining_matches, strengths, avg_goals)

    # Générer tous les scores d'un coup (nb_sim x nb_matches)
    all_goals_a = rng.poisson(lambdas_a, size=(nb_sim, nb_matches))
    all_goals_b = rng.poisson(lambdas_b, size=(nb_sim, nb_matches))

    # Résoudre les égalités par re-tirage
    draws = all_goals_a == all_goals_b
    while draws.any():
        all_goals_a[draws] = rng.poisson(np.broadcast_to(lambdas_a, (nb_sim, nb_matches))[draws])
        all_goals_b[draws] = rng.poisson(np.broadcast_to(lambdas_b, (nb_sim, nb_matches))[draws])
        draws = all_goals_a == all_goals_b

    # Accumuler points, buts marqués, buts encaissés
    base_pts = np.array([standings[t] for t in teams], dtype=np.int64)
    pts = np.tile(base_pts, (nb_sim, 1))
    gf = np.zeros((nb_sim, nb_teams), dtype=np.int64)
    ga = np.zeros((nb_sim, nb_teams), dtype=np.int64)

    for m in range(nb_matches):
        home, away = remaining_matches[m]
        ih, ia = team_idx[home], team_idx[away]
        goals_h, goals_a = all_goals_a[:, m], all_goals_b[:, m]

        gf[:, ih] += goals_h
        ga[:, ih] += goals_a
        gf[:, ia] += goals_a
        ga[:, ia] += goals_h

        home_wins = goals_h > goals_a
        pts[:, ih] += np.where(home_wins, 3, 0)
        pts[:, ia] += np.where(~home_wins, 3, 0)

    # Classement : -points, -diff buts, -buts marqués, aléatoire (départage)
    goal_diff = gf - ga
    tiebreak = rng.random((nb_sim, nb_teams))

    position_counter: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}
    for sim in range(nb_sim):
        order = np.lexsort((tiebreak[sim], -gf[sim], -goal_diff[sim], -pts[sim]))
        for pos, team_i in enumerate(order):
            position_counter[teams[team_i]][pos] += 1

    return position_counter


def simulate_monte_carlo(
    nb_simulations: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
    strengths: dict[str, int] | None = None,
    avg_goals: float = 4.5,
) -> dict[str, list[int]]:
    """Simulation Monte Carlo single-thread avec scores Poisson."""
    teams = list(standings.keys())
    if strengths is None:
        strengths = {t: 50 for t in teams}

    rng = np.random.default_rng()
    return _run_simulation(nb_simulations, standings, remaining_matches, strengths, avg_goals, rng)


# --- Version multiprocessing ---


def _worker(
    nb_sim: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
    strengths: dict[str, int],
    avg_goals: float,
    seed_entropy: int | Sequence[int] | None,
) -> dict[str, list[int]]:
    """Worker exécuté dans un processus séparé avec son propre RNG."""
    rng = np.random.default_rng(seed_entropy)
    return _run_simulation(nb_sim, standings, remaining_matches, strengths, avg_goals, rng)


def simulate_monte_carlo_mp(
    nb_simulations: int,
    standings: dict[str, int],
    remaining_matches: list[tuple[str, str]],
    strengths: dict[str, int] | None = None,
    avg_goals: float = 4.5,
) -> dict[str, list[int]]:
    """Simulation Monte Carlo répartie sur tous les coeurs CPU.

    Utilise SeedSequence pour garantir des flux RNG indépendants.
    """
    teams = list(standings.keys())
    nb_teams = len(teams)
    if strengths is None:
        strengths = {t: 50 for t in teams}

    num_workers = cpu_count() or 4
    chunk_size = nb_simulations // num_workers
    remainder = nb_simulations % num_workers

    ss = np.random.SeedSequence()
    child_seeds = ss.spawn(num_workers)

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(
                _worker,
                chunk_size + (1 if i < remainder else 0),
                standings,
                remaining_matches,
                strengths,
                avg_goals,
                child_seeds[i].entropy,
            )
            for i in range(num_workers)
        ]
        results = [f.result() for f in futures]

    merged: dict[str, list[int]] = {t: [0] * nb_teams for t in teams}
    for result in results:
        for team in teams:
            for pos in range(nb_teams):
                merged[team][pos] += result[team][pos]

    return merged
