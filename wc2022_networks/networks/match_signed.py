"""Signed match-result network builder."""

from __future__ import annotations

import pandas as pd

from ..data import column_lookup, resolve_team_column


def build_match_signed_edges(matches: pd.DataFrame) -> pd.DataFrame:
    lookup = column_lookup(matches)
    rows = []
    for match_id, match in matches.iterrows():
        goals_1 = int(match[resolve_team_column(lookup, "number of goals", 1)])
        goals_2 = int(match[resolve_team_column(lookup, "number of goals", 2)])
        rows.append(
            {
                "match_id": match_id + 1,
                "source": match["team1"],
                "target": match["team2"],
                "weight": goals_1 - goals_2,
                "source_goals": goals_1,
                "target_goals": goals_2,
                "date": match["date"],
                "stage": match["category"],
            }
        )
    return pd.DataFrame(rows)

