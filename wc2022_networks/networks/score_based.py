"""Shared builders for score-based World Cup 2022 networks."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from ..config import OFFENSIVE_EFFICIENCY_FEATURES, PRESSURE_RECOVERY_FEATURES


def build_score_edges_from_team_matches(
    team_matches: pd.DataFrame,
    features: list[str],
    network_name: str,
) -> pd.DataFrame:
    differentials = defaultdict(list)
    by_match = {
        match_id: group.set_index("team")
        for match_id, group in team_matches.groupby("match_id", sort=True)
    }

    for group in by_match.values():
        if len(group) != 2:
            continue
        team_a, team_b = group.index.tolist()
        for feature in features:
            differentials[feature].append(float(group.loc[team_a, feature] - group.loc[team_b, feature]))

    scales = {}
    for feature, values in differentials.items():
        scale = float(np.std(values))
        scales[feature] = scale if scale > 1e-9 else 1.0

    rows = []
    for match_id, group in by_match.items():
        if len(group) != 2:
            continue
        team_a, team_b = group.index.tolist()
        score = 0.0
        contributions = {}
        for feature in features:
            contribution = float(group.loc[team_a, feature] - group.loc[team_b, feature]) / scales[feature]
            contributions[f"{feature}_z_diff"] = contribution
            score += contribution
        score /= len(features)

        if score >= 0:
            source = team_a
            target = team_b
            weight = score
        else:
            source = team_b
            target = team_a
            weight = -score

        rows.append(
            {
                "match_id": match_id,
                "source": source,
                "target": target,
                "weight": weight,
                "raw_score_team1_minus_team2": score,
                "network": network_name,
                "date": group.iloc[0]["date"],
                "stage": group.iloc[0]["stage"],
                **contributions,
            }
        )
    return pd.DataFrame(rows)


def build_offensive_efficiency_edges(team_matches: pd.DataFrame) -> pd.DataFrame:
    return build_score_edges_from_team_matches(
        team_matches,
        OFFENSIVE_EFFICIENCY_FEATURES,
        "offensive_efficiency",
    )


def build_pressure_recovery_edges(team_matches: pd.DataFrame) -> pd.DataFrame:
    return build_score_edges_from_team_matches(
        team_matches,
        PRESSURE_RECOVERY_FEATURES,
        "pressure_recovery",
    )


def aggregate_directed_edges(edges: pd.DataFrame) -> pd.DataFrame:
    if edges.empty:
        return pd.DataFrame(columns=["source", "target", "weight", "edge_count"])
    return (
        edges.groupby(["source", "target"], as_index=False)
        .agg(weight=("weight", "sum"), edge_count=("weight", "size"))
        .sort_values(["source", "target"])
    )
