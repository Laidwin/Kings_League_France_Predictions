# Kings League France Predictions

Simulateur de classements finaux de la Kings League France par méthodes probabilistes.

A partir du classement actuel et des matchs restants, le programme calcule la probabilité que chaque équipe termine à chaque position du classement final.

## Méthodes de simulation

| Méthode             | Description                                                   |
| ------------------- | ------------------------------------------------------------- |
| `monte_carlo_mp`    | Monte Carlo avec scores Poisson, multiprocessing (par défaut) |
| `monte_carlo`       | Monte Carlo single-thread                                     |
| `deterministic`     | Tirage aléatoire de résultats discrets (victoire/défaite)     |
| `exhaustive`        | Énumération de tous les scénarios possibles                   |
| `exhaustive_mp`     | Exhaustive avec multiprocessing                               |

## Installation

```bash
git clone https://github.com/Laidwin/Kings_League_France_Predictions.git
cd Kings_League_France_Predictions
uv sync
```

## Utilisation

Chaque journée est configurée dans un fichier TOML sous `data/` :

```bash
# Lancer la simulation pour la journée 6 (saison 1)
python main.py data/journee_6.toml

# Surcharger la méthode ou le nombre de simulations
python main.py data/journee_6.toml --method deterministic --simulations 100000

# Ne générer que le CSV (sans heatmap)
python main.py data/journee_6.toml --no-heatmap
```

Le programme peut aussi être lancé via le module ou l'entry point :

```bash
python -m kings_league data/journee_6.toml
kings-league-predict data/journee_6.toml
```

## Configuration

Les fichiers TOML supportent deux modes pour les matchs restants :

**Liste explicite** (journées avancées) :

```toml
[matchday]
name = "Kings League France - 2024-2025 Split 1 Journée 6"
season = "2024-2025"
split = 1
journee = 6

[simulation]
method = "monte_carlo_mp"
nb_simulations = 10_000_000

[standings]
"Unit3d" = 9
"Athletic Dragon Blanc" = 9

[[remaining_matches]]
home = "FC SILMI"
away = "PANAM ALL STARZ"
```

**Round-robin automatique** (début de saison) :

```toml
[matches]
mode = "round_robin"
played = [
    ["Wolf Pack FC", "FC SILMI"],
    ["Unit3d", "Athletic Dragon Blanc"],
]
```

## Résultats

### 2025-2026 — Split 1

#### Journée 1

![Journée 1](result/2025-2026/split_1/J1.png)

#### Journée 2

![Journée 2](result/2025-2026/split_1/J2.png)

#### Journée 3

![Journée 3](result/2025-2026/split_1/J3.png)

### Historique

- [Résultats](result/README.md)

## Sources

- [Kings League France](https://kingsleague.pro/fr/france)

## Licence

MIT — voir [LICENSE](LICENSE).
