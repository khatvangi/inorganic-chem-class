import json
import networkx as nx
from networkx.algorithms import community
import urllib.request

INPUT_FILE = "data/context_graph.json"
OUTPUT_FILE = "data/suggested_curriculum.json"
OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma2:9b"  # Using the stronger model for better synthesis

def query_llm(prompt):
    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": MODEL, 
        "prompt": prompt, 
        "stream": False
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['response'].strip()
    except Exception as e:
        print(f"    Error querying LLM: {e}")
        return None

def get_module_identity(concepts):
    # Take top 15 concepts to avoid overwhelming the context window if the cluster is huge
    top_concepts = concepts[:20]
    
    prompt = f"""
    You are an expert Inorganic Chemistry Curriculum Designer.
    Analyze the following list of concepts extracted from a textbook corpus.
    Determine the specific "Course Topic" or "Chapter Title" they belong to.

    CONCEPTS:
    {', '.join(top_concepts)}

    INSTRUCTIONS:
    1. Output ONLY the topic title (e.g., "Crystal Field Theory", "Organometallic Catalysis", "Group 14 Elements").
    2. If the concepts are too random, vague, or unrelated to form a coherent topic, output "DROP".
    3. Do NOT use specific molecule names as the title (e.g., don't say "Carbon & Lead", say "Group 14 Chemistry").
    4. Keep it concise (2-5 words).
    """
    
    return query_llm(prompt)

def main():
    print(f"Loading graph from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    G = nx.Graph()
    for link in data['links']:
        G.add_edge(link['source'], link['target'])

    print("Detecting concept communities...")
    # Using Greedy Modularity Communities
    communities = list(community.greedy_modularity_communities(G))
    print(f"Found {len(communities)} raw clusters.")
    
    curriculum = []
    
    print("Analyzing clusters with LLM to identify Topics...")
    for i, comm in enumerate(communities):
        # Sort concepts by connectivity within the cluster (centrality)
        concepts = sorted(list(comm), key=lambda x: G.degree(x), reverse=True)
        
        # Filter tiny noise clusters immediately
        if len(concepts) < 4: 
            continue
        
        print(f"  Processing Cluster {i+1} (Size: {len(concepts)})...")
        
        # Ask LLM for a title
        title = get_module_identity(concepts)
        
        if not title:
            print("    -> LLM failed, skipping.")
            continue
            
        clean_title = title.replace('"', '').replace("'", "").strip()
        
        if "DROP" in clean_title or len(clean_title) < 3:
            print(f"    -> Dropped (Noise): {clean_title}")
            continue

        print(f"    -> Identified: {clean_title}")
        
        module = {
            "id": f"module_{i+1}",
            "title": clean_title,
            "concepts": concepts[:12], # Store top 12 for context
            "size": len(concepts)
        }
        curriculum.append(module)

    # Sort modules by size (proxy for importance/breadth)
    curriculum.sort(key=lambda x: x['size'], reverse=True)
    
    # Save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(curriculum, f, indent=2)
        
    print(f"\nSaved {len(curriculum)} validated modules to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
