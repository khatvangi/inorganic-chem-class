import json
import networkx as nx
import matplotlib.pyplot as plt

INPUT_FILE = "data/context_graph.json"
OUTPUT_PDF = "data/context_graph.pdf"

def main():
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    # Build Graph
    G = nx.Graph()
    for node in data['nodes']:
        G.add_node(node['id'])
    for link in data['links']:
        G.add_edge(link['source'], link['target'])

    # Filter for the largest connected component to make the PDF readable
    # (The full 170-component graph is too scattered)
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    largest_component = G.subgraph(components[0])
    
    print(f"Graph has {G.number_of_nodes()} nodes.")
    print(f"Plotting largest component ({largest_component.number_of_nodes()} nodes) for clarity...")

    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(largest_component, k=0.15, iterations=20)
    
    nx.draw_networkx_nodes(largest_component, pos, node_size=50, node_color="skyblue", alpha=0.7)
    nx.draw_networkx_edges(largest_component, pos, alpha=0.3)
    
    # Draw labels for high-degree nodes only
    labels = {}
    for node in largest_component.nodes():
        if largest_component.degree(node) > 1:
            labels[node] = node
            
    nx.draw_networkx_labels(largest_component, pos, labels, font_size=8, font_color="black")

    plt.title("Emergent Context Graph (Largest Cluster)", fontsize=16)
    plt.axis("off")
    
    plt.savefig(OUTPUT_PDF, format="pdf", bbox_inches="tight")
    print(f"Saved PDF to {OUTPUT_PDF}")

if __name__ == "__main__":
    main()
