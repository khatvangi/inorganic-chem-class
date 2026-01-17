import json
import networkx as nx
from collections import Counter

INPUT_FILE = "data/context_graph.json"

def main():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Build NetworkX Graph
    G = nx.Graph() # Undirected for simple connectivity
    
    for node in data['nodes']:
        G.add_node(node['id'])
        
    for link in data['links']:
        G.add_edge(link['source'], link['target'], label=link.get('label', 'related'))

    print(f"--- Graph Analysis ---")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    # 1. Degree Centrality (Hubs)
    degree_dict = dict(G.degree(G.nodes()))
    sorted_degree = sorted(degree_dict.items(), key=lambda item: item[1], reverse=True)
    
    print("\n--- Top 15 Concept Hubs (Degree Centrality) ---")
    for concept, degree in sorted_degree[:15]:
        print(f"{degree:<4} | {concept}")

    # 2. Betweenness Centrality (Bridges)
    # Measures how often a node acts as a bridge along the shortest path between two other nodes.
    betweenness = nx.betweenness_centrality(G)
    sorted_betweenness = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Top 10 'Bridge' Concepts (Betweenness) ---")
    for concept, score in sorted_betweenness[:10]:
        if score > 0.001: # Filter noise
            print(f"{score:.4f} | {concept}")

    # 3. Relationship Types
    relations = [link.get('label', '').lower() for link in data['links']]
    common_relations = Counter(relations).most_common(10)
    
    print("\n--- Top Relationship Types ---")
    for rel, count in common_relations:
        print(f"{count:<4} | {rel}")

    # 4. Component Analysis (Islands)
    components = list(nx.connected_components(G))
    print(f"\n--- Structure ---")
    print(f"Number of disconnected components: {len(components)}")
    print(f"Size of largest component: {len(components[0])} nodes")
    
    # List a few small islands
    if len(components) > 1:
        print("\nSample Small Islands (Disconnected Topics):")
        for comp in components[1:6]:
            print(f"  - {list(comp)}")

if __name__ == "__main__":
    main()
