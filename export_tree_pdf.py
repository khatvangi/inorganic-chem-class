import json
import networkx as nx
import matplotlib.pyplot as plt

INPUT_FILE = "data/learning_tree.json"
OUTPUT_PDF = "data/learning_tree.pdf"

def main():
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    G = nx.DiGraph()
    
    # Add nodes (Modules)
    for node in data['nodes']:
        # Rename long titles for PDF
        label = node['title']
        if len(label) > 20:
            label = label[:20] + "..."
        G.add_node(node['title'], label=label)
        
    # Add Edges
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'])

    print(f"Tree has {G.number_of_nodes()} modules and {G.number_of_edges()} dependencies.")

    plt.figure(figsize=(12, 8))
    
    # Use hierarchical layout logic (shell or spectral as fallback)
    try:
        pos = nx.planar_layout(G)
    except:
        pos = nx.spring_layout(G, k=0.5)
        
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#e0f2fe", edgecolors="#2563eb")
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color="gray")
    
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=9)

    plt.title("Emergent Learning Tree (Prerequisites)", fontsize=14)
    plt.axis("off")
    
    plt.savefig(OUTPUT_PDF, format="pdf", bbox_inches="tight")
    print(f"Saved PDF to {OUTPUT_PDF}")

if __name__ == "__main__":
    main()
