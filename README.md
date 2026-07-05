# Network-Based Analysis of Team Performance in the FIFA World Cup 2022

This project analyses the FIFA World Cup 2022 as a set of networks built from
match-level performance statistics. Each national team is represented as a node,
while edges represent different football relationships: match results,
statistical dominance, attacking efficiency, pressure/recovery, and playing-style
similarity.

The goal is to show that a football tournament can be studied through multiple
network views, where changing the meaning of an edge changes the question being
answered.

## Authors

- Rui Coelho, up202106772
- Tiago Figueiredo, up202104640

## Project Overview

The input dataset contains 64 matches and 32 teams from the FIFA World Cup 2022.
Starting from the raw match table, the pipeline builds:

| Network | Type | Edge meaning |
| --- | --- | --- |
| Signed match network | Directed signed | `team1 -> team2`; weight is goal difference |
| Outcome network | Directed weighted | Defeated team points to winner; draws are reciprocal |
| Statistical dominance network | Directed weighted | More statistically dominant team points to opponent |
| Offensive efficiency network | Directed weighted | More efficient attacking team points to opponent |
| Pressure/recovery network | Directed weighted | Stronger pressure/recovery team points to opponent |
| Style similarity network | Undirected weighted | Teams are linked by similar average performance profiles |

The analysis uses weighted PageRank, weighted degree/strength, graph density,
connected components, clustering coefficient, cosine similarity, and weighted
label propagation for style communities.

## Main Findings

- Argentina ranks 1st in the outcome PageRank network, followed by France.
- France leads the traditional points ranking, but PageRank rewards Argentina's
  tournament path and final result.
- Tunisia and Saudi Arabia rise in outcome PageRank because they defeated France
  and Argentina, respectively.
- Argentina, Brazil, Spain, England, and Germany rank highest in statistical
  dominance.
- The Netherlands leads offensive efficiency.
- Morocco leads pressure/recovery, followed by Japan.
- The style similarity network separates teams into interpretable groups,
  including high-output teams, possession/progression profiles, wide/offensive
  profiles, and reactive or transition-oriented teams.

The key conclusion is that tournament success, statistical control, attacking
conversion, defensive disruption, and playing style are related but not the same
thing.

## Repository Structure

```text
.
├── world_cup_2022/
│   └── Fifa_world_cup_matches.csv      # Raw input dataset
├── wc2022_networks/
│   ├── config.py                       # Constants and feature lists
│   ├── data.py                         # Data cleaning and team-level tables
│   ├── metrics.py                      # PageRank, components, clustering, communities
│   ├── outputs.py                      # Full pipeline orchestration
│   ├── plots.py                        # Figure generation
│   └── networks/
│       ├── match_signed.py             # Signed result network
│       ├── outcome.py                  # Outcome/PageRank edge construction
│       ├── statistical_dominance.py    # Dominance edge construction
│       ├── score_based.py              # Efficiency and pressure/recovery networks
│       └── style_similarity.py         # Style similarity network
├── figures/                            # Figures used in the report
├── paper/
│   ├── world_cup_2022_network_analysis.tex
│   └── world_cup_2022_network_analysis.pdf
├── world_cup_2022_networks.py          # CLI entry point
├── requirements.txt
└── README.md
```

Generated CSVs are not stored in the repository. They can be regenerated from
the raw dataset by running the pipeline.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The project uses:

- `pandas` for tabular data processing
- `numpy` for numerical operations, PageRank matrices, z-scores, cosine
  similarity, and SVD layout support
- `matplotlib` for plots

Graph algorithms are implemented directly in the project code; the project does
not require `networkx`.

## Running the Analysis

Run the full pipeline with the default input and output paths:

```bash
python3 world_cup_2022_networks.py
```

By default, this reads:

```text
world_cup_2022/Fifa_world_cup_matches.csv
```

and writes generated outputs to:

```text
outputs/world_cup_2022/
```

You can also provide explicit paths:

```bash
python3 world_cup_2022_networks.py \
  --input world_cup_2022/Fifa_world_cup_matches.csv \
  --output outputs/world_cup_2022
```

The output directory contains:

```text
outputs/world_cup_2022/
├── tables/
│   ├── team_match_table.csv
│   ├── team_summary.csv
│   ├── team_rankings.csv
│   ├── team_rankings_by_points.csv
│   ├── team_rankings_by_outcome_pagerank.csv
│   ├── team_rankings_by_statistical_dominance.csv
│   ├── team_rankings_by_offensive_efficiency.csv
│   ├── team_rankings_by_pressure_recovery.csv
│   ├── network_metrics.csv
│   ├── style_features.csv
│   └── style_communities.csv
├── networks/
│   ├── match_signed_edges.csv
│   ├── outcome_edges_by_match.csv
│   ├── outcome_edges_aggregated.csv
│   ├── statistical_dominance_edges_by_match.csv
│   ├── statistical_dominance_edges_aggregated.csv
│   ├── offensive_efficiency_edges_by_match.csv
│   ├── offensive_efficiency_edges_aggregated.csv
│   ├── pressure_recovery_edges_by_match.csv
│   ├── pressure_recovery_edges_aggregated.csv
│   └── style_similarity_edges.csv
└── figures/
    ├── top_outcome_pagerank.png
    ├── points_vs_statistical_dominance.png
    ├── top_offensive_efficiency.png
    ├── top_pressure_recovery.png
    ├── efficiency_vs_pressure_recovery.png
    ├── style_similarity_network.png
    └── team_performance_heatmap.png
```

## Method Summary

### Outcome PageRank

The outcome network models competitive success. If team A beats team B, the edge
is `B -> A` with weight 3. If the match is a draw, both teams point to each other
with weight 1.


Weighted PageRank is then applied with damping factor 0.85. This means a team is
ranked highly not only because it won matches, but because it received result
support from teams that are themselves important.

### Statistical Dominance

The dominance network compares teams using normalized match-statistic
differences:

- possession
- total attempts
- attempts on target
- attempts inside the penalty area
- completed passes
- corners
- completed line breaks
- completed defensive line breaks
- forced turnovers
- defensive pressures applied

Each feature difference is standardized, then averaged. The edge points from the
more dominant team to the opponent.

### Offensive Efficiency

The offensive efficiency network focuses on conversion instead of volume. It uses:

- goals per attempt
- goals per attempt on target
- shot accuracy
- goals per completed pass

The edge points from the more efficient attacking team to the less efficient
opponent.

### Pressure and Recovery

The pressure/recovery network measures defensive disruption through:

- defensive pressures applied
- forced turnovers

The edge points from the team with the stronger pressure/recovery profile to the
opponent.

### Style Similarity

The style network compares average team profiles. Features are standardized and
teams are linked using cosine similarity. Each team connects to its four nearest
neighbours, and the graph is symmetrized.

Weighted label propagation is then used to detect style communities.

## Report

The full written report is available at:

```text
paper/world_cup_2022_network_analysis.pdf
```

The LaTeX source is available at:

```text
paper/world_cup_2022_network_analysis.tex
```

## Notes and Limitations

- The analysis is based on a small tournament sample: some teams played only 3
  matches, while finalists played 7.
- Knockout-stage penalty shootouts are not modelled separately unless encoded in
  the original score columns.
- Match stage is stored and summarized, but the main rankings do not apply
  explicit stage weights.
- The generated CSVs are derived artifacts. The raw CSV and Python code are
  sufficient to reproduce them.
