"""Data loading, cleaning, and team-level table builders."""

from __future__ import annotations

import re

import pandas as pd

from .config import DOMINANCE_FEATURES, STAGE_ORDER, STYLE_FEATURES


def normalize_column_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def column_lookup(df: pd.DataFrame) -> dict[str, str]:
    lookup = {}
    for col in df.columns:
        lookup[normalize_column_name(col)] = col
    return lookup


def resolve_team_column(lookup: dict[str, str], feature: str, side: int) -> str:
    normalized_feature = normalize_column_name(feature)
    candidates = [
        f"{normalized_feature} team{side}",
        f"{normalized_feature}team{side}",
    ]
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    raise KeyError(f"Could not resolve column for feature={feature!r}, side={side}")


def parse_value(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    text = str(value).strip()
    if text.endswith("%"):
        text = text[:-1]
    if text == "":
        return float("nan")
    return float(text)


def safe_div(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def ensure_numeric_match_data(df: pd.DataFrame) -> pd.DataFrame:
    lookup = column_lookup(df)
    numeric_columns = [
        "number of goals",
        "conceded",
        "assists",
        "yellow cards",
        "red cards",
        "fouls against",
        "offsides",
        "penalties scored",
        "goal preventions",
        "own goals",
    ] + sorted(set(STYLE_FEATURES + DOMINANCE_FEATURES))

    result = df.copy()
    for feature in numeric_columns:
        for side in (1, 2):
            col = resolve_team_column(lookup, feature, side)
            result[col] = result[col].map(parse_value)
    return result


def result_label(goals_for: int, goals_against: int) -> str:
    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def build_team_match_table(matches: pd.DataFrame) -> pd.DataFrame:
    lookup = column_lookup(matches)
    rows = []
    for match_id, match in matches.iterrows():
        for side, opp_side in ((1, 2), (2, 1)):
            team = match[f"team{side}"]
            opponent = match[f"team{opp_side}"]
            goals_for = int(match[resolve_team_column(lookup, "number of goals", side)])
            goals_against = int(match[resolve_team_column(lookup, "number of goals", opp_side)])
            row = {
                "match_id": match_id + 1,
                "team": team,
                "opponent": opponent,
                "date": match["date"],
                "hour": match["hour"],
                "stage": match["category"],
                "stage_order": STAGE_ORDER.get(match["category"], 0),
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_diff": goals_for - goals_against,
                "result": result_label(goals_for, goals_against),
                "points": 3 if goals_for > goals_against else 1 if goals_for == goals_against else 0,
            }
            for feature in STYLE_FEATURES:
                row[feature] = match[resolve_team_column(lookup, feature, side)]
            row["pass_completion_rate"] = (
                row["passes completed"] / row["passes"] if row["passes"] else 0.0
            )
            row["cross_completion_rate"] = (
                row["crosses completed"] / row["crosses"] if row["crosses"] else 0.0
            )
            row["shot_accuracy"] = (
                row["on target attempts"] / row["total attempts"]
                if row["total attempts"]
                else 0.0
            )
            row["goals_per_attempt"] = safe_div(row["goals_for"], row["total attempts"])
            row["goals_per_on_target"] = safe_div(row["goals_for"], row["on target attempts"])
            row["goals_per_completed_pass"] = safe_div(row["goals_for"], row["passes completed"])
            rows.append(row)
    return pd.DataFrame(rows)


def build_team_summary(team_matches: pd.DataFrame) -> pd.DataFrame:
    summary = (
        team_matches.groupby("team")
        .agg(
            matches=("match_id", "count"),
            wins=("result", lambda s: int((s == "W").sum())),
            draws=("result", lambda s: int((s == "D").sum())),
            losses=("result", lambda s: int((s == "L").sum())),
            points=("points", "sum"),
            goals_for=("goals_for", "sum"),
            goals_against=("goals_against", "sum"),
            goal_diff=("goal_diff", "sum"),
            max_stage_order=("stage_order", "max"),
            avg_possession=("possession", "mean"),
            avg_total_attempts=("total attempts", "mean"),
            avg_on_target_attempts=("on target attempts", "mean"),
            avg_passes_completed=("passes completed", "mean"),
            avg_pass_completion_rate=("pass_completion_rate", "mean"),
            avg_corners=("corners", "mean"),
            avg_completed_line_breaks=("completed line breaks", "mean"),
            avg_forced_turnovers=("forced turnovers", "mean"),
            avg_defensive_pressures=("defensive pressures applied", "mean"),
            avg_goals_per_attempt=("goals_per_attempt", "mean"),
            avg_goals_per_on_target=("goals_per_on_target", "mean"),
            avg_shot_accuracy=("shot_accuracy", "mean"),
        )
        .reset_index()
    )
    summary["stage_reached"] = summary["max_stage_order"].map(
        {
            1: "Group Stage",
            2: "Round of 16",
            3: "Quarter-final",
            4: "Semi-final",
            5: "Third-place match",
            6: "Final",
        }
    )
    summary = summary.sort_values(
        ["points", "goal_diff", "goals_for", "matches"], ascending=[False, False, False, False]
    )
    summary.insert(0, "points_rank", range(1, len(summary) + 1))
    return summary

