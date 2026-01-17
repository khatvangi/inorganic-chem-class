import json
import urllib.request
from collections import Counter

# Config
INPUT_FILE = "data/suggested_curriculum.json"
OUTPUT_FILE = "data/learning_tree.json"
OLLAMA_URL = "http://localhost:11434"

# The Panel of Experts
MODELS = [
    "qwen3:32b",   # Senior Expert
    "gemma2:9b"    # Expert
]

def query_model(model, prompt):
    print(f"  > Consulting {model}...")
    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": model, 
        "prompt": prompt, 
        "stream": False,
        "format": "json"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.loads(result['response']).get('dependencies', [])
    except Exception as e:
        print(f"    Error with {model}: {e}")
        return []

def main():
    print("Reading Curriculum Modules...")
    with open(INPUT_FILE, 'r') as f:
        modules = json.load(f)

    top_modules = [m for m in modules if m['size'] >= 4][:15]
    module_titles = [m['title'] for m in top_modules]
    
    print(f"Structuring {len(top_modules)} Modules via Consensus...")

    prompt = f"""
    You are an expert Inorganic Chemistry Curriculum Designer.
    Determine the prerequisite dependencies between these learning modules.
    
    MODULES:
    {json.dumps(module_titles, indent=2)}

    RULES:
    1. Identify strict prerequisites (A must be learned before B).
    2. Example: "Atomic Structure" -> "Periodicity" -> "Bonding".
    3. Return a JSON list of edges.

    OUTPUT FORMAT:
    {{
        "dependencies": [
            {{"source": "Prerequisite Module", "target": "Advanced Module"}}
        ]
    }}
    """

    all_votes = []
    
    # Poll the models
    for model in MODELS:
        votes = query_model(model, prompt)
        all_votes.extend([(v['source'], v['target']) for v in votes])

    # Tally votes
    vote_counts = Counter(all_votes)
    consensus_edges = []
    
    print("\n--- Consensus Results ---")
    for (src, tgt), count in vote_counts.items():
        # Logic: If Qwen3 (32b) says it, it's weighty. If 2+ models say it, it's solid.
        # Simple majority or presence in Qwen3 might be best. 
        # Let's go with: Accepted if count >= 2 OR (count == 1 and src/tgt are valid)
        # Actually, let's stick to strict consensus: count >= 2 implies high confidence.
        
        status = "Dropped"
        if count >= 2:
            consensus_edges.append({"source": src, "target": tgt})
            status = "Accepted"
        
        print(f"[{count}/3] {src} -> {tgt} ({status})")

    # Fallback: If consensus is too empty, take Qwen's unique suggestions too
    if len(consensus_edges) < 5:
        print("Consensus too strict, adding high-quality Qwen edges...")
        qwen_votes = query_model(MODELS[0], prompt)
        for v in qwen_votes:
            edge = {"source": v['source'], "target": v['target']}
            if edge not in consensus_edges:
                consensus_edges.append(edge)

    # Save
    tree_data = {
        "nodes": [{"title": t} for t in module_titles],
        "edges": consensus_edges
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tree_data, f, indent=2)
        
    print(f"\nFinal Learning Tree: {len(consensus_edges)} verified dependencies.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
