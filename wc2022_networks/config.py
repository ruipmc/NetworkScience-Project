"""Constants used by the World Cup 2022 network generators."""

from __future__ import annotations

from pathlib import Path


INPUT_DEFAULT = Path("world_cup_2022/Fifa_world_cup_matches.csv")
OUTPUT_DEFAULT = Path("outputs/world_cup_2022")


STAGE_ORDER = {
    "Group A": 1,
    "Group B": 1,
    "Group C": 1,
    "Group D": 1,
    "Group E": 1,
    "Group F": 1,
    "Group G": 1,
    "Group H": 1,
    "Round of 16": 2,
    "Quarter-final": 3,
    "Semi-final": 4,
    "Play-off for third place": 5,
    "Final": 6,
}


STYLE_FEATURES = [
    "possession",
    "total attempts",
    "on target attempts",
    "attempts inside the penalty area",
    "attempts outside the penalty area",
    "passes",
    "passes completed",
    "crosses",
    "crosses completed",
    "switches of play completed",
    "corners",
    "attempted line breaks",
    "completed line breaks",
    "attempted defensive line breaks",
    "completed defensive line breaks",
    "forced turnovers",
    "defensive pressures applied",
]


DOMINANCE_FEATURES = [
    "possession",
    "total attempts",
    "on target attempts",
    "attempts inside the penalty area",
    "passes completed",
    "corners",
    "completed line breaks",
    "completed defensive line breaks",
    "forced turnovers",
    "defensive pressures applied",
]


OFFENSIVE_EFFICIENCY_FEATURES = [
    "goals_per_attempt",
    "goals_per_on_target",
    "shot_accuracy",
    "goals_per_completed_pass",
]


PRESSURE_RECOVERY_FEATURES = [
    "defensive pressures applied",
    "forced turnovers",
]


TEAM_ABBREVIATIONS = {
    "ARGENTINA": "ARG",
    "AUSTRALIA": "AUS",
    "BELGIUM": "BEL",
    "BRAZIL": "BRA",
    "CAMEROON": "CMR",
    "CANADA": "CAN",
    "COSTA RICA": "CRC",
    "CROATIA": "CRO",
    "DENMARK": "DEN",
    "ECUADOR": "ECU",
    "ENGLAND": "ENG",
    "FRANCE": "FRA",
    "GERMANY": "GER",
    "GHANA": "GHA",
    "IRAN": "IRN",
    "JAPAN": "JPN",
    "KOREA REPUBLIC": "KOR",
    "MEXICO": "MEX",
    "MOROCCO": "MAR",
    "NETHERLANDS": "NED",
    "POLAND": "POL",
    "PORTUGAL": "POR",
    "QATAR": "QAT",
    "SAUDI ARABIA": "KSA",
    "SENEGAL": "SEN",
    "SERBIA": "SRB",
    "SPAIN": "ESP",
    "SWITZERLAND": "SUI",
    "TUNISIA": "TUN",
    "UNITED STATES": "USA",
    "URUGUAY": "URU",
    "WALES": "WAL",
}

