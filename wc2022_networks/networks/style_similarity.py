"""Style-similarity network builder."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import STYLE_FEATURES


def build_style_similarity_edges(
    team_matches: pd.DataFrame,
    teams: list[str],
    k_neighbors: int = 4,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    features = STYLE_FEATURES + [
        "pass_completion_rate",
        "cross_completion_rate",
        "shot_accuracy",
    ]
    team_features = team_matches.groupby("team")[features].mean().reindex(teams)
    values = team_features.to_numpy(dtype=float)
    means = values.mean(axis=0)
    stds = values.std(axis=0)
    stds[stds < 1e-9] = 1.0
    z = (values - means) / stds
    norms = np.linalg.norm(z, axis=1)
    norms[norms < 1e-9] = 1.0
    similarity = (z @ z.T) / np.outer(norms, norms)
    np.fill_diagonal(similarity, -np.inf)

    edges = {}
    for i, source in enumerate(teams):
        neighbors = np.argsort(similarity[i])[-k_neighbors:]
        for j in neighbors:
            if not np.isfinite(similarity[i, j]):
                continue
            target = teams[j]
            a, b = sorted((source, target))
            edges[(a, b)] = max(edges.get((a, b), -1.0), float(similarity[i, j]))

    rows = [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(edges.items())
    ]
    edge_df = pd.DataFrame(rows)
    feature_df = team_features.reset_index()
    return edge_df, feature_df, z

