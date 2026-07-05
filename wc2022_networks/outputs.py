"""Output orchestration for the World Cup 2022 network analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import build_team_match_table, build_team_summary, ensure_numeric_match_data
from .metrics import (
    build_network_metrics,
    directed_degree_table,
    label_propagation_communities,
    weighted_pagerank,
)
from .networks.match_signed import build_match_signed_edges
from .networks.outcome import build_outcome_edges
from .networks.score_based import (
    aggregate_directed_edges,
    build_offensive_efficiency_edges,
    build_pressure_recovery_edges,
)
from .networks.statistical_dominance import build_statistical_dominance_edges
from .networks.style_similarity import build_style_similarity_edges
from .plots import (
    plot_efficiency_vs_pressure,
    plot_points_vs_dominance,
    plot_style_similarity_network,
    plot_team_feature_heatmap,
    plot_top_metric,
    plot_top_pagerank,
)


def write_outputs(input_csv: Path, output_dir: Path) -> None:
    tables_dir = output_dir / "tables"
    networks_dir = output_dir / "networks"
    figures_dir = output_dir / "figures"
    for directory in (tables_dir, networks_dir, figures_dir):
        directory.mkdir(parents=True, exist_ok=True)

    matches = pd.read_csv(input_csv)
    matches = ensure_numeric_match_data(matches)
    teams = sorted(set(matches["team1"]) | set(matches["team2"]))

    team_matches = build_team_match_table(matches)
    team_summary = build_team_summary(team_matches)
    match_signed_edges = build_match_signed_edges(matches)
    outcome_edges_raw = build_outcome_edges(matches)
    stat_edges_raw = build_statistical_dominance_edges(matches)
    offensive_edges_raw = build_offensive_efficiency_edges(team_matches)
    pressure_edges_raw = build_pressure_recovery_edges(team_matches)
    outcome_edges = aggregate_directed_edges(outcome_edges_raw)
    stat_edges = aggregate_directed_edges(stat_edges_raw)
    offensive_edges = aggregate_directed_edges(offensive_edges_raw)
    pressure_edges = aggregate_directed_edges(pressure_edges_raw)
    style_edges, style_features, z_features = build_style_similarity_edges(team_matches, teams)
    style_communities = label_propagation_communities(teams, style_edges)

    outcome_pagerank = weighted_pagerank(teams, outcome_edges).rename(
        columns={"pagerank": "outcome_pagerank", "pagerank_rank": "outcome_pagerank_rank"}
    )
    stat_edges_for_pagerank = stat_edges.rename(columns={"source": "target", "target": "source"})
    stat_pagerank = weighted_pagerank(teams, stat_edges_for_pagerank).rename(
        columns={"pagerank": "stat_pagerank", "pagerank_rank": "stat_pagerank_rank"}
    )
    outcome_degree = directed_degree_table(teams, outcome_edges, "outcome")
    stat_degree = directed_degree_table(teams, stat_edges, "stat")
    offensive_degree = directed_degree_table(teams, offensive_edges, "offensive")
    pressure_degree = directed_degree_table(teams, pressure_edges, "pressure")

    rankings = (
        team_summary.merge(outcome_pagerank, on="team")
        .merge(stat_pagerank, on="team")
        .merge(outcome_degree, on="team")
        .merge(stat_degree, on="team")
        .merge(offensive_degree, on="team")
        .merge(pressure_degree, on="team")
        .merge(style_communities, on="team")
    )
    rankings = rankings.rename(columns={"stat_net_strength": "stat_received_minus_dominant"})
    rankings["stat_net_dominance"] = rankings["stat_out_strength"] - rankings["stat_in_strength"]
    rankings = rankings.rename(
        columns={
            "offensive_net_strength": "offensive_received_minus_efficient",
            "pressure_net_strength": "pressure_received_minus_recovery",
        }
    )
    rankings["offensive_net_efficiency"] = (
        rankings["offensive_out_strength"] - rankings["offensive_in_strength"]
    )
    rankings["pressure_net_recovery"] = (
        rankings["pressure_out_strength"] - rankings["pressure_in_strength"]
    )
    rankings = rankings.sort_values(["outcome_pagerank_rank", "points_rank", "team"])

    metrics = build_network_metrics(
        teams,
        outcome_edges,
        stat_edges,
        offensive_edges,
        pressure_edges,
        style_edges,
    )

    team_matches.to_csv(tables_dir / "team_match_table.csv", index=False)
    team_summary.to_csv(tables_dir / "team_summary.csv", index=False)
    rankings.to_csv(tables_dir / "team_rankings.csv", index=False)
    rankings.sort_values(["points_rank", "team"]).to_csv(
        tables_dir / "team_rankings_by_points.csv", index=False
    )
    rankings.sort_values(["outcome_pagerank_rank", "team"]).to_csv(
        tables_dir / "team_rankings_by_outcome_pagerank.csv", index=False
    )
    rankings.sort_values(["stat_net_dominance", "points"], ascending=[False, False]).to_csv(
        tables_dir / "team_rankings_by_statistical_dominance.csv", index=False
    )
    rankings.sort_values(["offensive_net_efficiency", "points"], ascending=[False, False]).to_csv(
        tables_dir / "team_rankings_by_offensive_efficiency.csv", index=False
    )
    rankings.sort_values(["pressure_net_recovery", "points"], ascending=[False, False]).to_csv(
        tables_dir / "team_rankings_by_pressure_recovery.csv", index=False
    )
    metrics.to_csv(tables_dir / "network_metrics.csv", index=False)
    style_features.to_csv(tables_dir / "style_features.csv", index=False)
    style_communities.to_csv(tables_dir / "style_communities.csv", index=False)

    match_signed_edges.to_csv(networks_dir / "match_signed_edges.csv", index=False)
    outcome_edges_raw.to_csv(networks_dir / "outcome_edges_by_match.csv", index=False)
    outcome_edges.to_csv(networks_dir / "outcome_edges_aggregated.csv", index=False)
    stat_edges_raw.to_csv(networks_dir / "statistical_dominance_edges_by_match.csv", index=False)
    stat_edges.to_csv(networks_dir / "statistical_dominance_edges_aggregated.csv", index=False)
    offensive_edges_raw.to_csv(networks_dir / "offensive_efficiency_edges_by_match.csv", index=False)
    offensive_edges.to_csv(networks_dir / "offensive_efficiency_edges_aggregated.csv", index=False)
    pressure_edges_raw.to_csv(networks_dir / "pressure_recovery_edges_by_match.csv", index=False)
    pressure_edges.to_csv(networks_dir / "pressure_recovery_edges_aggregated.csv", index=False)
    style_edges.to_csv(networks_dir / "style_similarity_edges.csv", index=False)

    plot_top_pagerank(rankings, figures_dir)
    plot_points_vs_dominance(rankings, figures_dir)
    plot_top_metric(
        rankings,
        "offensive_net_efficiency",
        "Top teams by offensive efficiency",
        "Net offensive efficiency",
        "top_offensive_efficiency.png",
        figures_dir,
        "#b45f06",
    )
    plot_top_metric(
        rankings,
        "pressure_net_recovery",
        "Top teams by pressure/recovery",
        "Net pressure/recovery",
        "top_pressure_recovery.png",
        figures_dir,
        "#2f6f73",
    )
    plot_efficiency_vs_pressure(rankings, figures_dir)
    plot_style_similarity_network(teams, z_features, style_edges, style_communities, figures_dir)
    plot_team_feature_heatmap(rankings, style_features, figures_dir)

    print(f"Input: {input_csv}")
    print(f"Teams: {len(teams)}")
    print(f"Matches: {len(matches)}")
    print(f"Output directory: {output_dir}")
    print("Generated:")
    print(f"  tables: {tables_dir}")
    print(f"  networks: {networks_dir}")
    print(f"  figures: {figures_dir}")
