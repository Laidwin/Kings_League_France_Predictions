"""Chargement et validation de la configuration d'une journée."""

import tomllib
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


@dataclass(frozen=True)
class MatchdayConfig:
    """Configuration complète d'une journée de simulation."""

    season: str
    split: int
    journee: int
    standings: dict[str, int]
    goal_diff: dict[str, int]
    remaining_matches: list[tuple[str, str]]
    strengths: dict[str, int]
    method: str = "monte_carlo_mp"
    nb_simulations: int = 1_000_000
    avg_goals: float = 4.5

    @property
    def name(self) -> str:
        return f"Kings League France - {self.season.replace('-', '/')} - Split {self.split} - Journée {self.journee}"

    @property
    def teams(self) -> list[str]:
        return list(self.standings.keys())

    @property
    def nb_teams(self) -> int:
        return len(self.standings)


def load_config(path: Path) -> MatchdayConfig:
    """Charge une configuration depuis un fichier TOML."""
    with open(path, "rb") as f:
        data = tomllib.load(f)

    matchday = data["matchday"]
    standings: dict[str, int] = data["standings"]
    teams = list(standings.keys())

    # Strengths : valeurs explicites ou 50 (neutre) par défaut
    raw_strengths = data.get("strengths", {})
    strengths = {team: raw_strengths.get(team, 50) for team in teams}

    # Matchs restants : liste explicite ou round-robin moins les matchs joués
    matches_cfg = data.get("matches", {})
    mode = matches_cfg.get("mode", "explicit")

    # Différence de buts initiale depuis les matchs joués
    goal_diff: dict[str, int] = {team: 0 for team in teams}

    if mode == "round_robin":
        raw_played = matches_cfg.get("played", [])
        # Support ancien format (listes) et nouveau format (dicts avec scores)
        if raw_played and isinstance(raw_played[0], dict):
            played = set()
            for m in raw_played:
                played.add((m["home"], m["away"]))
                if "score" in m:
                    gh, ga = m["score"]
                    goal_diff[m["home"]] += gh - ga
                    goal_diff[m["away"]] += ga - gh
        else:
            played = {tuple(m) for m in raw_played}
        remaining_matches = [(a, b) for a, b in combinations(teams, 2) if (a, b) not in played and (b, a) not in played]
    else:
        remaining_matches = [(m["home"], m["away"]) for m in data.get("remaining_matches", [])]

    # Simulation
    sim = data.get("simulation", {})

    return MatchdayConfig(
        season=str(matchday["season"]),
        split=int(matchday["split"]),
        journee=int(matchday["journee"]),
        standings=standings,
        goal_diff=goal_diff,
        remaining_matches=remaining_matches,
        strengths=strengths,
        method=sim.get("method", "monte_carlo_mp"),
        nb_simulations=sim.get("nb_simulations", 1_000_000),
        avg_goals=sim.get("avg_goals", 4.5),
    )
