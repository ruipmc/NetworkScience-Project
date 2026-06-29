"""Pressure/recovery network builder."""

from __future__ import annotations

import pandas as pd

from ..config import PRESSURE_RECOVERY_FEATURES
from .common import build_score_edges_from_team_matches


def build_pressure_recovery_edges(team_matches: pd.DataFrame) -> pd.DataFrame:
    return build_score_edges_from_team_matches(
        team_matches,
        PRESSURE_RECOVERY_FEATURES,
        "pressure_recovery",
    )

