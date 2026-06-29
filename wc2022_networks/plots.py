"""Figure builders for the World Cup 2022 network analysis."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import TEAM_ABBREVIATIONS


def plot_top_pagerank(rankings: pd.DataFrame, figures_dir: Path) -> None:
    top = rankings.sort_values("outcome_pagerank", ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top["team"][::-1], top["outcome_pagerank"][::-1], color="#315c8c")
    ax.set_xlabel("Outcome PageRank")
    ax.set_title("Top teams by outcome-based PageRank")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / "top_outcome_pagerank.png", dpi=220)
    plt.close(fig)


def plot_points_vs_dominance(rankings: pd.DataFrame, figures_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.8))
    ax.scatter(rankings["points"], rankings["stat_net_dominance"], s=70, color="#8f3f2f")
    for row in rankings.itertuples(index=False):
        ax.annotate(
            TEAM_ABBREVIATIONS.get(row.team, row.team[:3]),
            (row.points, row.stat_net_dominance),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )
    ax.set_xlabel("Tournament points")
    ax.set_ylabel("Net statistical dominance")
    ax.set_title("Tournament points vs statistical dominance")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / "points_vs_statistical_dominance.png", dpi=220)
    plt.close(fig)


def plot_top_metric(
    rankings: pd.DataFrame,
    metric: str,
    title: str,
    xlabel: str,
    filename: str,
    figures_dir: Path,
    color: str,
) -> None:
    top = rankings.sort_values(metric, ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top["team"][::-1], top[metric][::-1], color=color)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / filename, dpi=220)
    plt.close(fig)


def plot_efficiency_vs_pressure(rankings: pd.DataFrame, figures_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.8))
    ax.scatter(
        rankings["offensive_net_efficiency"],
        rankings["pressure_net_recovery"],
        s=70,
        color="#356859",
    )
    for row in rankings.itertuples(index=False):
        ax.annotate(
            TEAM_ABBREVIATIONS.get(row.team, row.team[:3]),
            (row.offensive_net_efficiency, row.pressure_net_recovery),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )
    ax.set_xlabel("Net offensive efficiency")
    ax.set_ylabel("Net pressure/recovery")
    ax.set_title("Offensive efficiency vs pressure/recovery")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / "efficiency_vs_pressure_recovery.png", dpi=220)
    plt.close(fig)


def plot_style_similarity_network(
    teams: list[str],
    z_features: np.ndarray,
    style_edges: pd.DataFrame,
    communities: pd.DataFrame,
    figures_dir: Path,
) -> None:
    _, _, vt = np.linalg.svd(z_features, full_matrices=False)
    coords = z_features @ vt[:2].T
    x = coords[:, 0]
    y = coords[:, 1]
    x = (x - x.mean()) / (x.std() if x.std() > 1e-9 else 1.0)
    y = (y - y.mean()) / (y.std() if y.std() > 1e-9 else 1.0)
    pos = {team: (x[i], y[i]) for i, team in enumerate(teams)}
    community_by_team = dict(zip(communities["team"], communities["style_community"]))
    color_map = plt.get_cmap("tab10")

    fig, ax = plt.subplots(figsize=(9, 7))
    weights = style_edges["weight"].to_numpy(dtype=float)
    min_w = float(weights.min()) if len(weights) else 0.0
    max_w = float(weights.max()) if len(weights) else 1.0
    span = max(max_w - min_w, 1e-9)

    for row in style_edges.itertuples(index=False):
        sx, sy = pos[row.source]
        tx, ty = pos[row.target]
        alpha = 0.18 + 0.45 * ((row.weight - min_w) / span)
        ax.plot([sx, tx], [sy, ty], color="#6b7280", linewidth=0.8, alpha=alpha, zorder=1)

    for team in teams:
        cx, cy = pos[team]
        community = community_by_team.get(team, 0)
        ax.scatter(
            cx,
            cy,
            s=130,
            color=color_map((community - 1) % 10),
            edgecolor="white",
            linewidth=0.8,
            zorder=2,
        )
        ax.text(
            cx,
            cy + 0.08,
            TEAM_ABBREVIATIONS.get(team, team[:3]),
            ha="center",
            va="bottom",
            fontsize=8,
            zorder=3,
        )

    ax.set_title("Style similarity network")
    ax.set_xlabel("Style component 1")
    ax.set_ylabel("Style component 2")
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(figures_dir / "style_similarity_network.png", dpi=240)
    plt.close(fig)


def plot_team_feature_heatmap(
    rankings: pd.DataFrame,
    style_features: pd.DataFrame,
    figures_dir: Path,
) -> None:
    selected = [
        "possession",
        "total attempts",
        "on target attempts",
        "passes completed",
        "corners",
        "completed line breaks",
        "forced turnovers",
        "defensive pressures applied",
    ]
    ordered_teams = rankings.sort_values("points_rank")["team"].tolist()
    feature_table = style_features.set_index("team").loc[ordered_teams, selected]
    values = feature_table.to_numpy(dtype=float)
    means = values.mean(axis=0)
    stds = values.std(axis=0)
    stds[stds < 1e-9] = 1.0
    z = (values - means) / stds

    fig, ax = plt.subplots(figsize=(9.5, 8))
    image = ax.imshow(z, aspect="auto", cmap="RdBu_r", vmin=-2.2, vmax=2.2)
    ax.set_yticks(range(len(ordered_teams)))
    ax.set_yticklabels([TEAM_ABBREVIATIONS.get(team, team[:3]) for team in ordered_teams], fontsize=8)
    ax.set_xticks(range(len(selected)))
    ax.set_xticklabels(
        [
            "Poss.",
            "Attempts",
            "On target",
            "Passes",
            "Corners",
            "Line breaks",
            "Turnovers",
            "Pressures",
        ],
        rotation=35,
        ha="right",
    )
    ax.set_title("Standardized average team-performance profile")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    fig.tight_layout()
    fig.savefig(figures_dir / "team_performance_heatmap.png", dpi=240)
    plt.close(fig)

