"""Statistical dominance network builder."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from ..config import DOMINANCE_FEATURES
from ..data import column_lookup, resolve_team_column


def build_statistical_dominance_edges(matches: pd.DataFrame) -> pd.DataFrame:
    lookup = column_lookup(matches)
    differentials = defaultdict(list)
    for _, match in matches.iterrows():
        for feature in DOMINANCE_FEATURES:
            v1 = match[resolve_team_column(lookup, feature, 1)]
            v2 = match[resolve_team_column(lookup, feature, 2)]
            differentials[feature].append(float(v1 - v2))

    scales = {}
    for feature, values in differentials.items():
        scale = float(np.std(values))
        scales[feature] = scale if scale > 1e-9 else 1.0

    rows = []
    for match_id, match in matches.iterrows():
        score = 0.0
        contributions = {}
        for feature in DOMINANCE_FEATURES:
            v1 = match[resolve_team_column(lookup, feature, 1)]
            v2 = match[resolve_team_column(lookup, feature, 2)]
            contribution = float(v1 - v2) / scales[feature]
            contributions[f"{feature}_z_diff"] = contribution
            score += contribution
        score /= len(DOMINANCE_FEATURES)

        if score >= 0:
            source = match["team1"]
            target = match["team2"]
            weight = score
        else:
            source = match["team2"]
            target = match["team1"]
            weight = -score

        rows.append(
            {
                "match_id": match_id + 1,
                "source": source,
                "target": target,
                "weight": weight,
                "raw_score_team1_minus_team2": score,
                "date": match["date"],
                "stage": match["category"],
                **contributions,
            }
        )
    return pd.DataFrame(rows)

