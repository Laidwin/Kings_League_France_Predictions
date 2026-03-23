"""Interface en ligne de commande."""

import argparse
from pathlib import Path
from time import time

from kings_league.config import MatchdayConfig, load_config
from kings_league.deterministic import simulate_deterministic
from kings_league.exhaustive import simulate_exhaustive, simulate_exhaustive_mp
from kings_league.monte_carlo import simulate_monte_carlo, simulate_monte_carlo_mp
from kings_league.visualization import build_dataframe, export_csv, generate_heatmap, print_table

METHODS = {
    "deterministic": "Déterministe",
    "monte_carlo": "Monte Carlo",
    "monte_carlo_mp": "Monte Carlo (multiprocessing)",
    "exhaustive": "Exhaustive",
    "exhaustive_mp": "Exhaustive (multiprocessing)",
}

RESULT_DIR = Path(__file__).parent.parent / "result"


def run_simulation(config: MatchdayConfig) -> tuple[dict[str, list[int]], int]:
    """Exécute la simulation selon la méthode configurée."""
    match config.method:
        case "deterministic":
            counter = simulate_deterministic(config.nb_simulations, config.standings, config.remaining_matches)
            return counter, config.nb_simulations

        case "monte_carlo":
            counter = simulate_monte_carlo(
                config.nb_simulations,
                config.standings,
                config.remaining_matches,
                strengths=config.strengths,
                avg_goals=config.avg_goals,
                goal_diff=config.goal_diff,
            )
            return counter, config.nb_simulations

        case "monte_carlo_mp":
            counter = simulate_monte_carlo_mp(
                config.nb_simulations,
                config.standings,
                config.remaining_matches,
                strengths=config.strengths,
                avg_goals=config.avg_goals,
                goal_diff=config.goal_diff,
            )
            return counter, config.nb_simulations

        case "exhaustive":
            return simulate_exhaustive(config.standings, config.remaining_matches)

        case "exhaustive_mp":
            return simulate_exhaustive_mp(config.standings, config.remaining_matches)

        case _:
            raise ValueError(f"Méthode inconnue : {config.method}. Méthodes disponibles : {', '.join(METHODS)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kings-league-predict",
        description="Simulateur de classements Kings League France",
    )
    parser.add_argument("config", type=Path, help="Fichier de configuration TOML de la journée")
    parser.add_argument("--method", choices=METHODS, help="Méthode de simulation (surcharge le fichier config)")
    parser.add_argument("--simulations", type=int, help="Nombre de simulations (surcharge le fichier config)")
    parser.add_argument("--no-heatmap", action="store_true", help="Ne pas générer la heatmap")
    args = parser.parse_args()

    # Charger la configuration
    config = load_config(args.config)

    # Appliquer les surcharges CLI
    overrides: dict = {}
    if args.method:
        overrides["method"] = args.method
    if args.simulations:
        overrides["nb_simulations"] = args.simulations
    if overrides:
        config = MatchdayConfig(**{**config.__dict__, **overrides})

    method_label = METHODS.get(config.method, config.method)
    print(f"=== {config.name} ===")
    print(f"Méthode : {method_label}")
    print(f"Matchs restants : {len(config.remaining_matches)}")
    print(f"Simulations : {config.nb_simulations:,}")
    print()

    # Simulation
    start = time()
    position_counter, nb_simulations = run_simulation(config)
    elapsed = time() - start
    print(f"Simulation terminée en {elapsed:.1f}s ({nb_simulations:,} scénarios)\n")

    # Résultats
    df = build_dataframe(position_counter, nb_simulations)
    print_table(df)

    # Export dans result/{season}/split_{split}/J{journee}.*
    output_dir = RESULT_DIR / config.season / f"split_{config.split}"
    export_csv(df, output_dir / f"J{config.journee}.csv")

    if not args.no_heatmap:
        generate_heatmap(
            df,
            output_dir / f"J{config.journee}.png",
            title=f"Simulation des classements - {config.name}",
        )
