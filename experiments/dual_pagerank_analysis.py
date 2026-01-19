#!/usr/bin/env python3
"""
Dual PageRank Curriculum Analysis

This script implements the methodology described in DUAL_PAGERANK_MODEL.md
and JCE_PAPER_PACKAGE.md for analyzing knowledge graph structure.

Key findings:
- Forward PageRank identifies CAPSTONES (teach last)
- Reverse PageRank identifies FOUNDATIONS (teach first)
- For sparse graphs (mean degree < 3), degree-based analysis is more appropriate

Usage:
    python dual_pagerank_analysis.py [--graph PATH]

Author: Kiran Brahma + Claude
Date: January 2026
"""

import json
import argparse
from collections import Counter
from pathlib import Path

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx not installed. Install with: pip install networkx")


def load_knowledge_graph(path: str) -> dict:
    """Load knowledge graph from JSON file."""
    with open(path) as f:
        return json.load(f)


def build_networkx_graph(kg_data: dict) -> 'nx.DiGraph':
    """Convert knowledge graph JSON to NetworkX DiGraph."""
    if not HAS_NETWORKX:
        raise ImportError("networkx required")

    G = nx.DiGraph()

    # add nodes
    for node in kg_data.get('nodes', []):
        G.add_node(node['id'], **{k: v for k, v in node.items() if k != 'id'})

    # add edges (source is prerequisite for target)
    for edge in kg_data.get('edges', []):
        G.add_edge(edge['source'], edge['target'])

    return G


def analyze_graph_sparsity(G: 'nx.DiGraph') -> dict:
    """
    Analyze graph sparsity metrics.

    Returns dict with:
    - node_count, edge_count
    - mean_degree
    - in_degree_zero_count (pure sources)
    - out_degree_zero_count (pure sinks)
    """
    n = G.number_of_nodes()
    e = G.number_of_edges()

    in_degrees = [G.in_degree(node) for node in G.nodes()]
    out_degrees = [G.out_degree(node) for node in G.nodes()]

    return {
        'node_count': n,
        'edge_count': e,
        'mean_degree': (2 * e) / n if n > 0 else 0,
        'in_degree_zero_count': sum(1 for d in in_degrees if d == 0),
        'in_degree_zero_pct': sum(1 for d in in_degrees if d == 0) / n * 100 if n > 0 else 0,
        'out_degree_zero_count': sum(1 for d in out_degrees if d == 0),
        'out_degree_zero_pct': sum(1 for d in out_degrees if d == 0) / n * 100 if n > 0 else 0,
    }


def dual_pagerank_curriculum(G: 'nx.DiGraph', alpha: float = 0.85) -> dict:
    """
    Compute curriculum position using dual PageRank.

    Args:
        G: DiGraph where edge (A, B) means "A is prerequisite for B"
        alpha: PageRank damping factor

    Returns:
        dict: {node: {'foundation_score', 'capstone_score', 'position', 'category'}}
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required")

    # forward PR: what many things lead TO (capstones)
    pr_forward = nx.pagerank(G, alpha=alpha)

    # reverse PR: what IS prerequisite for many (foundations)
    pr_reverse = nx.pagerank(G.reverse(), alpha=alpha)

    result = {}
    for node in G.nodes():
        fwd = pr_forward.get(node, 0)
        rev = pr_reverse.get(node, 0)
        position = rev - fwd

        # categorize based on position
        if position > 0.001:
            category = "FOUNDATION"
        elif position < -0.005:
            category = "CAPSTONE"
        else:
            category = "BRIDGE"

        result[node] = {
            'foundation_score': rev,
            'capstone_score': fwd,
            'position': position,
            'category': category
        }

    return result


def degree_based_curriculum(G: 'nx.DiGraph') -> dict:
    """
    Alternative analysis for sparse graphs using degree directly.

    More appropriate when mean_degree < 3.

    Returns:
        dict with 'foundations', 'capstones', 'hubs' lists
    """
    foundations = []  # in=0, out>0
    capstones = []    # out=0, in>0
    hubs = []         # in>2 and out>2

    for node in G.nodes():
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)

        if in_deg == 0 and out_deg > 0:
            foundations.append((node, out_deg))
        elif out_deg == 0 and in_deg > 0:
            capstones.append((node, in_deg))

        if in_deg > 2 and out_deg > 2:
            hubs.append((node, in_deg, out_deg))

    return {
        'foundations': sorted(foundations, key=lambda x: -x[1]),
        'capstones': sorted(capstones, key=lambda x: -x[1]),
        'hubs': sorted(hubs, key=lambda x: -(x[1] + x[2]))
    }


def print_analysis_report(G: 'nx.DiGraph'):
    """Print full analysis report."""

    print("=" * 60)
    print("DUAL PAGERANK CURRICULUM ANALYSIS")
    print("=" * 60)

    # sparsity analysis
    sparsity = analyze_graph_sparsity(G)
    print("\n## Graph Sparsity Metrics\n")
    print(f"  Nodes:              {sparsity['node_count']}")
    print(f"  Edges:              {sparsity['edge_count']}")
    print(f"  Mean degree:        {sparsity['mean_degree']:.2f}")
    print(f"  In-degree = 0:      {sparsity['in_degree_zero_count']} ({sparsity['in_degree_zero_pct']:.1f}%)")
    print(f"  Out-degree = 0:     {sparsity['out_degree_zero_count']} ({sparsity['out_degree_zero_pct']:.1f}%)")

    # recommendation
    print("\n## Method Recommendation\n")
    if sparsity['mean_degree'] < 3:
        print(f"  Mean degree {sparsity['mean_degree']:.2f} < 3 → Use DEGREE-BASED analysis")
        recommended = "degree"
    elif sparsity['mean_degree'] > 10:
        print(f"  Mean degree {sparsity['mean_degree']:.2f} > 10 → Use PAGERANK analysis")
        recommended = "pagerank"
    else:
        print(f"  Mean degree {sparsity['mean_degree']:.2f} in [3,10] → Compare both methods")
        recommended = "both"

    # dual pagerank analysis
    print("\n## Dual PageRank Analysis\n")
    pr_results = dual_pagerank_curriculum(G)

    categories = Counter(r['category'] for r in pr_results.values())
    total = sum(categories.values())

    print("  Category Distribution:")
    for cat in ['FOUNDATION', 'BRIDGE', 'CAPSTONE']:
        count = categories.get(cat, 0)
        pct = count / total * 100 if total > 0 else 0
        print(f"    {cat:12} {count:5} ({pct:5.1f}%)")

    # top foundations by pagerank
    foundations = [(n, r) for n, r in pr_results.items() if r['category'] == 'FOUNDATION']
    foundations.sort(key=lambda x: -x[1]['position'])

    print("\n  Top Foundations (by position score):")
    for name, data in foundations[:8]:
        print(f"    {name[:40]:40} pos={data['position']:+.5f}")

    # top capstones by pagerank
    capstones = [(n, r) for n, r in pr_results.items() if r['category'] == 'CAPSTONE']
    capstones.sort(key=lambda x: x[1]['position'])

    print("\n  Top Capstones (by position score):")
    for name, data in capstones[:8]:
        print(f"    {name[:40]:40} pos={data['position']:+.5f}")

    # degree-based analysis
    print("\n## Degree-Based Analysis (for sparse graphs)\n")
    degree_results = degree_based_curriculum(G)

    print(f"  Pure foundations (in=0, out>0): {len(degree_results['foundations'])}")
    print(f"  Pure capstones (out=0, in>0):   {len(degree_results['capstones'])}")
    print(f"  Hubs (in>2 and out>2):          {len(degree_results['hubs'])}")

    # actionable foundations (out >= 5)
    actionable = [(n, d) for n, d in degree_results['foundations'] if d >= 5]
    print(f"\n  Actionable Foundations (in=0, out>=5): {len(actionable)}")
    print("\n  Top 10 for diagnostic assessment:")
    for i, (name, out_deg) in enumerate(actionable[:10], 1):
        print(f"    {i:2}. {name[:40]:40} out={out_deg}")

    # top capstones by in-degree
    print("\n  Top Capstones (by in-degree):")
    for i, (name, in_deg) in enumerate(degree_results['capstones'][:8], 1):
        print(f"    {i:2}. {name[:40]:40} in={in_deg}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Dual PageRank Curriculum Analysis')
    parser.add_argument('--graph', type=str,
                        default='/storage/inorganic-chem-class/data/knowledge_graph.json',
                        help='Path to knowledge graph JSON')
    args = parser.parse_args()

    if not HAS_NETWORKX:
        print("Error: networkx is required. Install with: pip install networkx")
        return 1

    graph_path = Path(args.graph)
    if not graph_path.exists():
        print(f"Error: Graph file not found: {graph_path}")
        return 1

    print(f"Loading graph from: {graph_path}")
    kg_data = load_knowledge_graph(graph_path)
    G = build_networkx_graph(kg_data)

    print_analysis_report(G)

    return 0


if __name__ == '__main__':
    exit(main())
