"""Offensive efficiency network builder."""

from __future__ import annotations

import pandas as pd

from ..config import OFFENSIVE_EFFICIENCY_FEATURES
from .common import build_score_edges_from_team_matches


def build_offensive_efficiency_edges(team_matches: pd.DataFrame) -> pd.DataFrame:
    return build_score_edges_from_team_matches(
        team_matches,
        OFFENSIVE_EFFICIENCY_FEATURES,
        "offensive_efficiency",
    )

