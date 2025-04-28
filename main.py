from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from time import time
from PIL import Image
import matplotlib.offsetbox as offsetbox

from lib.methode_exhaustive_multiprocessing import methode_exhaustive_multiprocessing
from lib.methode_exhaustive import methode_exhaustive
from lib.methode_deterministe import methode_deterministe
from lib.methode_monte_carlo import monte_carlo

def main() -> None:
    # Classement initial
    current_points: dict[str, int]  = {
        "Unit3d": 9,
        "F2R": 12,
        "PANAM ALL STARZ": 12,
        "Wolf Pack FC": 5,
        "KARASU": 6,
        "Generation Seven": 9,
        "360 Nation": 6,
        "FC SILMI": 1
    }

    # Matchs restants (format: (équipe à domicile, équipe à l’extérieur))
    remaining_matches: list[tuple[str, str]] = [
        ("KARASU", "Generation Seven"),
        ("Unit3d", "Wolf Pack FC"),
        ("F2R","FC SILMI"),
        ("360 Nation", "PANAM ALL STARZ"),
        ("FC SILMI", "KARASU"),
        ("PANAM ALL STARZ", "Unit3d"),
        ("Wolf Pack FC", "F2R"),
        ("Generation Seven", "360 Nation")
    ]

    team_colors: dict[str, list[str]] = {
        "360 Nation": ["#e6dbd0","#5e2b2e"],
        "F2R": ["#f6c480","#213353"],
        "FC SILMI": ["#1e1c1a","#b59f6a"],
        "Generation Seven": ["#ecca7f","#232f45"],
        "KARASU": ["#060607","#d62406"],
        "PANAM ALL STARZ": ["#e61d22","#2e70bb"],
        "Unit3d": ["#dedde0","#064ef2"],
        "Wolf Pack FC": ["#0a1e36","#6f9dc4"]
    }

    nb_simulations: int = 1000000 
    choose: int = int(input("Choisir la méthode de simulation (1: déterministe, 2: Monte Carlo, 3: exhaustive, 4: exhaustive multiprocessing): "))
    # Simulation exhaustive
    start: float = time()
    position_counter: dict[str, list[int]] = {}
    if choose == 1:
        print("Méthode déterministe choisie")
        position_counter = methode_deterministe(nb_simulations, current_points, remaining_matches)
    elif choose == 2:
        print("Méthode Monte Carlo choisie")
        position_counter = monte_carlo(nb_simulations, current_points, remaining_matches)
    elif choose == 3:
        print("Méthode exhaustive choisie")
        position_counter, nb_simulations = methode_exhaustive(current_points, remaining_matches)
    elif choose == 4:
        print("Méthode exhaustive multiprocessing choisie")
        position_counter, nb_simulations = methode_exhaustive_multiprocessing(current_points, remaining_matches)
    else:
        print("Méthode invalide choisie")
    end: float = time()
    print(f"\nSimulation terminée en {end - start:.1f} secondes")
    print(f"Scénarios simulés : {nb_simulations:,}")

    # Afficher les résultats
    print("Probabilités de classement final :\n")
    team: str
    for team in current_points.keys():
        probs: list[float] = [round((count / nb_simulations) * 100, 2) for count in position_counter[team]]
        print(f"{team} : {probs}")
        

    df: pd.DataFrame = pd.DataFrame(position_counter).T
    df.columns = [f"{i+1}ᵉ" for i in range(len(df.columns))]

    # Convertir les valeurs en pourcentages
    df = df.apply(lambda x: x / nb_simulations * 100)

    # Ajouter une colonne 'Classement moyen' pour trier les équipes
    df["Classement moyen"] = df.apply(lambda row: sum((i+1)*p for i, p in enumerate(row)) / 100, axis=1)
    df = df.sort_values("Classement moyen")
    df = df.drop(columns=["Classement moyen"])
    
    # Export CSV
    df.to_csv("./result/classement_kings_league_france_J5.csv")
    print("Fichier CSV généré : ./result/classement_kings_league_france_J5.csv")

    # Afficher la heatmap
    plt.figure(figsize=(48, 28))
    sns.set_theme(font_scale=4)
    sns.heatmap(
        df,
        annot=df.map(lambda v: f"{v:.1f}%"),
        fmt="",
        cmap=sns.color_palette("inferno", as_cmap=True),
        linewidths=1.2,
        linecolor="white",
        cbar=False,
        yticklabels=False
    )
    for i, team in enumerate(df.index):
        """mask = np.ones_like(df, dtype=bool)
        mask[i, :] = False
        cmap = LinearSegmentedColormap.from_list(f"{team}_cmap", team_colors[team])
        sns.heatmap(df, mask=mask, cmap=cmap, cbar=False, 
                    annot=df.map(lambda v: f"{v:.1f}%"), xticklabels=True, yticklabels=False,
                    linewidths=1.2, linecolor="white", fmt="", ax=plt.gca())"""
        logo = Image.open(f"./assets/logos/{df.index[i]}.png")
        logo = logo.resize((200, 200), Image.Resampling.LANCZOS)
        imagebox = offsetbox.OffsetImage(logo, zoom=1)
        ab = offsetbox.AnnotationBbox(imagebox, (0, i), frameon=False, xycoords='data', boxcoords="offset points", pad=0, xybox=(-100, -100))
        plt.gca().add_artist(ab)


    plt.title("Simulation des classements - Kings League France", fontsize=72, weight='bold', pad=15)
    plt.xlabel("Position finale")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig("result/classement_kings_league_france_J5.png", dpi=300)

if __name__ == "__main__":
    main()
