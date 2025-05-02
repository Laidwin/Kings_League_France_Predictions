from itertools import islice, product
from multiprocessing import Pool, cpu_count
from typing import Any

def simulate_chunk(args) -> dict[Any | str, list[int]]:
    """
    Simule une partie des résultats des matchs restants.
    
    Args:
        args: tuple contenant les paramètres nécessaires pour la simulation.

    Returns:
        dict[Any | str, list[int]]: Dictionnaire contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Unpack the arguments
    start:int 
    end:int 
    current_points:dict[str, int] 
    remaining_matches:list[tuple[str, str]] 
    teams:list[str] 
    match_outcomes:list[tuple[int, int]]
    start, end, current_points, remaining_matches, teams, match_outcomes = args
    
    # Compteur de positions finales pour chaque équipe
    local_counter:dict[Any | str, list[int]] = {team: [0] * len(teams) for team in teams}
    
    # Simulation des scénarios
    match_indices:islice[tuple[int, ...]] = islice(product(range(len(match_outcomes)), repeat=len(remaining_matches)), start, start+end)
    outcome_indices:tuple[int, ...]
    for outcome_indices in match_indices:
        points:dict[str, int] = current_points.copy()
        team1:str
        team2:str
        outcome_index:int
        for (team1, team2), outcome_index in zip(remaining_matches, outcome_indices):
            pts1:int
            pts2:int
            pts1, pts2 = match_outcomes[outcome_index]
            points[team1] += pts1
            points[team2] += pts2
        sorted_teams: list[tuple[str, int]] = sorted(points.items(), key=lambda x: (-x[1], x[0]))
        pos:int
        team:str
        for pos, (team, _) in enumerate(sorted_teams):
            local_counter[team][pos] += 1
    print(f'Final results {local_counter}')
    return local_counter
    
def merge_counters(counters: list[dict[Any | str, list[int]]], teams: list[str]) -> dict[str, list[int]]:
    """
    Fusionne les compteurs de positions finales de chaque processus.
    
    Args:
        counters: list[dict[Any | str, list[int]]]: Liste des compteurs de chaque processus.
        teams: list[str]: Liste des équipes.
    
    Returns:
        dict[str, list[int]]: Dictionnaire fusionné contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Compteur de positions finales pour chaque équipe
    merged: dict[str, list[int]] = {team: [0] * len(teams) for team in teams}
    counter: dict[Any | str, list[int]]
    for counter in counters:
        team:str
        for team in teams:
            pos:int
            for pos in range(len(teams)):
                merged[team][pos] += counter[team][pos]
    return merged

def methode_exhaustive_multiprocessing(current_points: dict[str, int], remaining_matches: list[tuple[str, str]]) -> dict[str, list[int]]:
    """
    Simule les résultats des matchs restants en utilisant la méthode exhaustive.
    
    Args:
        current_points (dict[str, int]): Dictionnaire contenant les points actuels de chaque équipe.
        remaining_matches (list[tuple[str, str]]): Liste des matchs restants à simuler.

    Returns:
        dict[str, list[int]]: Dictionnaire contenant le nombre de fois où chaque équipe a terminé à chaque position.
    """
    # Définition des équipes et issues possibles d’un match
    teams: list[str] = list(current_points.keys())
    match_outcomes: list[tuple[int, int]] = [(3, 0), (2, 1), (1, 2), (0, 3)]  # Victoire équipe1, nul équipe 1, nul équipe 2, victoire équipe2

    # Génération de toutes les combinaisons possibles de résultats
    total_scenarios: int = len(match_outcomes) ** len(remaining_matches)
    
    print(f"Nombre total de scénarios : {total_scenarios:,}")
    
    num_cores: int = cpu_count()
    chunk_size: int = total_scenarios // num_cores
    ranges: list[tuple[int, int]] = [(i * chunk_size, chunk_size) for i in range(num_cores)]
    ranges[-1] = (ranges[-1][0], total_scenarios - ranges[-1][0])
    print(ranges)

    args_list: list[tuple[int, int, dict[str, int], list[tuple[str, str]], list[str], list[tuple[int, int]]]] = [(start, end, current_points, remaining_matches, teams, match_outcomes) for start, end in ranges]

    with Pool(processes=num_cores) as pool:
        results: list[dict[Any | str, list[int]]] = pool.map(simulate_chunk, args_list)

    final_counter: dict[str, list[int]] = merge_counters(results, teams)

    return final_counter, total_scenarios