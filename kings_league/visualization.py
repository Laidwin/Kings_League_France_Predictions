"""Génération de la heatmap des probabilités de classement."""

from pathlib import Path

import matplotlib.offsetbox as offsetbox
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image

LOGO_DIR = Path(__file__).parent.parent / "assets" / "logos"


def build_dataframe(
    position_counter: dict[str, list[int]],
    nb_simulations: int,
) -> pd.DataFrame:
    """Convertit les compteurs de positions en DataFrame de pourcentages triés."""
    df = pd.DataFrame(position_counter).T
    df.columns = [f"{i + 1}ᵉ" for i in range(len(df.columns))]
    df = df.apply(lambda x: x / nb_simulations * 100)

    # Tri par classement moyen pondéré
    avg_rank = df.apply(lambda row: sum((i + 1) * p for i, p in enumerate(row)) / 100, axis=1)
    df = df.loc[avg_rank.sort_values().index]

    return df


def print_table(df: pd.DataFrame) -> None:
    """Affiche un tableau formaté des probabilités dans la console."""
    teams = list(df.index)
    positions = list(df.columns)
    max_team_len = max(len(t) for t in teams)

    # En-tête
    header = " " * (max_team_len + 2) + "  ".join(f"{p:>6}" for p in positions)
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)

    # Lignes
    for team in teams:
        values = "  ".join(f"{v:5.1f}%" for v in df.loc[team])
        print(f"  {team:<{max_team_len}}  {values}")

    print(separator)


def export_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Exporte le DataFrame en CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path)
    print(f"CSV exporté : {output_path}")


def generate_heatmap(df: pd.DataFrame, output_path: Path, title: str) -> None:
    """Génère et sauvegarde la heatmap des probabilités de classement."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(48, 28))
    sns.set_theme(font_scale=4)

    annot_labels = np.array([[f"{v:.1f}%" for v in row] for row in df.values])

    sns.heatmap(
        df,
        annot=annot_labels,
        fmt="",
        cmap=sns.color_palette("inferno", as_cmap=True),
        linewidths=1.2,
        linecolor="white",
        cbar=False,
        yticklabels=False,
        ax=ax,
    )

    # Logos des équipes sur l'axe Y
    for i, team in enumerate(df.index):
        logo_path = LOGO_DIR / f"{team}.png"
        if logo_path.exists():
            logo = Image.open(logo_path).resize((200, 200), Image.Resampling.LANCZOS)
            imagebox = offsetbox.OffsetImage(np.array(logo), zoom=1)
            ab = offsetbox.AnnotationBbox(
                imagebox,
                (0, i),
                frameon=False,
                xycoords="data",
                boxcoords="offset points",
                pad=0,
                xybox=(-100, -100),
            )
            ax.add_artist(ab)

    ax.set_title(title, fontsize=72, weight="bold", pad=15)
    ax.set_xlabel("Position finale", fontsize=48, labelpad=20)
    ax.tick_params(axis="x", rotation=0, labelsize=36)
    ax.tick_params(axis="y", rotation=0)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    print(f"Heatmap exportée : {output_path}")
