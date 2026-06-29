"""Ranking and graph metric helpers for World Cup 2022 networks."""

from __future__ import annotations

from collections import Counter, deque

import numpy as np
import pandas as pd


def weighted_pagerank(
    teams: list[str],
    edges: pd.DataFrame,
    damping: float = 0.85,
    max_iter: int = 500,
    tol: float = 1e-12,
) -> pd.DataFrame:
    n = len(teams)
    idx = {team: i for i, team in enumerate(teams)}
    adjacency = np.zeros((n, n), dtype=float)
    for row in edges.itertuples(index=False):
        if row.source in idx and row.target in idx:
            adjacency[idx[row.source], idx[row.target]] += max(float(row.weight), 0.0)

    row_sums = adjacency.sum(axis=1)
    transition = np.zeros_like(adjacency)
    for i in range(n):
        if row_sums[i] > 0:
            transition[i] = adjacency[i] / row_sums[i]
        else:
            transition[i] = 1.0 / n

    scores = np.full(n, 1.0 / n)
    teleport = np.full(n, 1.0 / n)
    for _ in range(max_iter):
        new_scores = (1.0 - damping) * teleport + damping * transition.T.dot(scores)
        if np.abs(new_scores - scores).sum() < tol:
            scores = new_scores
            break
        scores = new_scores

    result = pd.DataFrame({"team": teams, "pagerank": scores})
    result["pagerank_rank"] = result["pagerank"].rank(ascending=False, method="min").astype(int)
    return result.sort_values(["pagerank_rank", "team"])


def directed_degree_table(teams: list[str], edges: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out_degree = Counter()
    in_degree = Counter()
    out_strength = Counter()
    in_strength = Counter()
    for row in edges.itertuples(index=False):
        out_degree[row.source] += 1
        in_degree[row.target] += 1
        out_strength[row.source] += float(row.weight)
        in_strength[row.target] += float(row.weight)

    rows = []
    for team in teams:
        rows.append(
            {
                "team": team,
                f"{prefix}_out_degree": out_degree[team],
                f"{prefix}_in_degree": in_degree[team],
                f"{prefix}_out_strength": out_strength[team],
                f"{prefix}_in_strength": in_strength[team],
                f"{prefix}_net_strength": in_strength[team] - out_strength[team],
            }
        )
    return pd.DataFrame(rows)


def undirected_adjacency(teams: list[str], edges: pd.DataFrame) -> dict[str, dict[str, float]]:
    adj = {team: {} for team in teams}
    for row in edges.itertuples(index=False):
        weight = float(row.weight)
        adj[row.source][row.target] = adj[row.source].get(row.target, 0.0) + weight
        adj[row.target][row.source] = adj[row.target].get(row.source, 0.0) + weight
    return adj


def connected_components_undirected(teams: list[str], edges: pd.DataFrame) -> list[list[str]]:
    adj = undirected_adjacency(teams, edges)
    seen = set()
    components = []
    for team in teams:
        if team in seen:
            continue
        queue = deque([team])
        seen.add(team)
        component = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in adj[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components


def weak_components_directed(teams: list[str], edges: pd.DataFrame) -> list[list[str]]:
    undirected_edges = edges[["source", "target", "weight"]].copy()
    return connected_components_undirected(teams, undirected_edges)


def strong_components_directed(teams: list[str], edges: pd.DataFrame) -> list[list[str]]:
    outgoing = {team: [] for team in teams}
    incoming = {team: [] for team in teams}
    for row in edges.itertuples(index=False):
        outgoing[row.source].append(row.target)
        incoming[row.target].append(row.source)

    seen = set()
    order = []

    def dfs_first(node: str) -> None:
        seen.add(node)
        for neighbor in outgoing[node]:
            if neighbor not in seen:
                dfs_first(neighbor)
        order.append(node)

    for team in teams:
        if team not in seen:
            dfs_first(team)

    seen.clear()
    components = []

    def dfs_second(node: str, component: list[str]) -> None:
        seen.add(node)
        component.append(node)
        for neighbor in incoming[node]:
            if neighbor not in seen:
                dfs_second(neighbor, component)

    for team in reversed(order):
        if team not in seen:
            component = []
            dfs_second(team, component)
            components.append(sorted(component))
    return components


def average_clustering_undirected(teams: list[str], edges: pd.DataFrame) -> float:
    adj = undirected_adjacency(teams, edges)
    coefficients = []
    for team in teams:
        neighbors = list(adj[team])
        degree = len(neighbors)
        if degree < 2:
            coefficients.append(0.0)
            continue
        links = 0
        for i in range(degree):
            for j in range(i + 1, degree):
                if neighbors[j] in adj[neighbors[i]]:
                    links += 1
        coefficients.append((2.0 * links) / (degree * (degree - 1)))
    return float(np.mean(coefficients))


def label_propagation_communities(
    teams: list[str],
    edges: pd.DataFrame,
    max_iter: int = 100,
) -> pd.DataFrame:
    adj = undirected_adjacency(teams, edges)
    labels = {team: team for team in teams}
    for _ in range(max_iter):
        changed = False
        for team in teams:
            weights = Counter()
            for neighbor, weight in adj[team].items():
                weights[labels[neighbor]] += weight
            if not weights:
                continue
            best_weight = max(weights.values())
            best_labels = sorted(label for label, weight in weights.items() if weight == best_weight)
            chosen = best_labels[0]
            if chosen != labels[team]:
                labels[team] = chosen
                changed = True
        if not changed:
            break

    unique_labels = {label: i + 1 for i, label in enumerate(sorted(set(labels.values())))}
    return pd.DataFrame(
        {
            "team": teams,
            "style_community": [unique_labels[labels[team]] for team in teams],
            "style_community_label": [labels[team] for team in teams],
        }
    )


def build_network_metrics(
    teams: list[str],
    outcome_edges: pd.DataFrame,
    stat_edges: pd.DataFrame,
    offensive_edges: pd.DataFrame,
    pressure_edges: pd.DataFrame,
    style_edges: pd.DataFrame,
) -> pd.DataFrame:
    n = len(teams)
    metrics = []
    for name, edges in (
        ("Outcome PageRank network", outcome_edges),
        ("Statistical dominance network", stat_edges),
        ("Offensive efficiency network", offensive_edges),
        ("Pressure/recovery network", pressure_edges),
    ):
        weak_components = weak_components_directed(teams, edges)
        strong_components = strong_components_directed(teams, edges)
        metrics.append(
            {
                "network": name,
                "nodes": n,
                "edges": len(edges),
                "density": len(edges) / (n * (n - 1)),
                "avg_in_degree": len(edges) / n,
                "avg_out_degree": len(edges) / n,
                "weak_components": len(weak_components),
                "largest_weak_component": max(len(c) for c in weak_components),
                "strong_components": len(strong_components),
                "largest_strong_component": max(len(c) for c in strong_components),
                "avg_clustering": "",
            }
        )

    style_components = connected_components_undirected(teams, style_edges)
    metrics.append(
        {
            "network": "Style similarity network",
            "nodes": n,
            "edges": len(style_edges),
            "density": (2 * len(style_edges)) / (n * (n - 1)),
            "avg_in_degree": "",
            "avg_out_degree": "",
            "weak_components": len(style_components),
            "largest_weak_component": max(len(c) for c in style_components),
            "strong_components": "",
            "largest_strong_component": "",
            "avg_clustering": average_clustering_undirected(teams, style_edges),
        }
    )
    return pd.DataFrame(metrics)

