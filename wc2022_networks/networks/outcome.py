"""Outcome/PageRank network builder."""

from __future__ import annotations

import pandas as pd

from ..data import column_lookup, resolve_team_column


def build_outcome_edges(matches: pd.DataFrame) -> pd.DataFrame:
    lookup = column_lookup(matches)
    rows = []
    for match_id, match in matches.iterrows():
        team1 = match["team1"]
        team2 = match["team2"]
        goals_1 = int(match[resolve_team_column(lookup, "number of goals", 1)])
        goals_2 = int(match[resolve_team_column(lookup, "number of goals", 2)])
        margin = abs(goals_1 - goals_2)
        base = {
            "match_id": match_id + 1,
            "date": match["date"],
            "stage": match["category"],
            "team1_goals": goals_1,
            "team2_goals": goals_2,
            "goal_margin": margin,
        }
        if goals_1 > goals_2:
            rows.append({**base, "source": team2, "target": team1, "weight": 3.0, "result": "win"})
        elif goals_2 > goals_1:
            rows.append({**base, "source": team1, "target": team2, "weight": 3.0, "result": "win"})
        else:
            rows.append({**base, "source": team1, "target": team2, "weight": 1.0, "result": "draw"})
            rows.append({**base, "source": team2, "target": team1, "weight": 1.0, "result": "draw"})
    return pd.DataFrame(rows)

