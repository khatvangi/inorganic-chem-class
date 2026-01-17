import json
import os
import random
import urllib.request
import urllib.parse
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "gemma2:9b"
OUTPUT_JSON = "data/context_graph_full.json"
OUTPUT_HTML = "context_graph_full.html"
SAMPLES_PER_BOOK = 60  # Medium Scan (Optimized for timeout)

client = QdrantClient(url=QDRANT_URL)

def get_books():
    """Get list of unique PDF names"""
    books = set()
    offset = None
    while True:
        results, offset = client.scroll(
            collection_name=COLLECTION,
            scroll_filter=models.Filter(),
            limit=100,
            with_payload=["pdf_name"],
            with_vectors=False,
            offset=offset
        )
        for point in results:
            name = point.payload.get("pdf_name")
            if name: books.add(name)
        
        if offset is None: break
        if len(books) >= 10: break 
    
    return list(books)

def extract_triples(text):
    """Use LLM to extract context triples"""
    # Optimized prompt for speed and density
    prompt = f"""
    Extract strictly chemical knowledge from this text as JSON triples.
    
    TEXT:
    {text[:1200]}
    
    OUTPUT FORMAT:
    {{
        "triples": [
            {{"source": "Concept", "relation": "verb/preposition", "target": "Concept"}}
        ]
    }}
    """
    
    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": LLM_MODEL, 
        "prompt": prompt, 
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1} # Deterministic
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.loads(result['response']).get('triples', [])
    except Exception:
        return []

def main():
    print("--- Starting Context Graph Probe ---")
    
    books = get_books()
    print(f"Found {len(books)} books: {books}")
    
    all_triples = []
    
    for book in books:
        print(f"\nProcessing Book: {book}")
        
        # Get random chunks from this book
        # We scroll and filter, simpler than random ID guessing
        points, _ = client.scroll(
            collection_name=COLLECTION,
            scroll_filter=models.Filter(
                must=[models.FieldCondition(key="pdf_name", match=models.MatchValue(value=book))]
            ),
            limit=100, # Fetch a batch
            with_payload=True,
            with_vectors=False
        )
        
        if not points: continue
        
        # Randomly select a subset
        samples = random.sample(points, min(len(points), SAMPLES_PER_BOOK))
        
        for i, point in enumerate(samples):
            print(f"  > Analyzing Chunk {i+1}/{len(samples)}...")
            text = point.payload.get("text", "")
            if len(text) < 200: continue # Skip tiny chunks
            
            triples = extract_triples(text)
            print(f"    + Extracted {len(triples)} connections")
            all_triples.extend(triples)

    # Post-process into Graph Format (Nodes/Links)
    print("\n--- Building Graph Structure ---")
    nodes = set()
    links = []
    
    for t in all_triples:
        src = t.get('source')
        tgt = t.get('target')
        rel = t.get('relation')
        
        if src and tgt and rel:
            nodes.add(src)
            nodes.add(tgt)
            links.append({
                "source": src,
                "target": tgt,
                "label": rel
            })
            
    graph_data = {
        "nodes": [{"id": n, "label": n, "group": "chemistry"} for n in nodes],
        "links": links
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(graph_data, f, indent=2)
        
    print(f"Saved Graph: {len(nodes)} nodes, {len(links)} links to {OUTPUT_JSON}")
    
    # Generate Visualization
    generate_html(graph_data)

def generate_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Context Graph: Inorganic Chemistry</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #mynetwork {{
                width: 100%;
                height: 90vh;
                border: 1px solid lightgray;
                background: #f4f4f9;
            }}
            body {{ font-family: sans-serif; margin: 0; padding: 20px; }}
        </style>
    </head>
    <body>
        <h2>Emergent Context Graph</h2>
        <p>Generated from {len(data['links'])} contextual connections across {len(data['nodes'])} concepts.</p>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({json.dumps(data['nodes'])});
            var edges = new vis.DataSet({json.dumps(data['links'])});

            var container = document.getElementById('mynetwork');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    size: 10,
                    font: {{ size: 14 }}
                }},
                edges: {{
                    font: {{ size: 10, align: 'middle' }},
                    color: {{ color: '#848484', highlight: '#848484' }},
                    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                    smooth: {{ type: 'dynamic' }}
                }},
                physics: {{
                    stabilization: false,
                    barnesHut: {{
                        gravitationalConstant: -2000,
                        springConstant: 0.04
                    }}
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html_content)
    print(f"Saved Visualization to {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
