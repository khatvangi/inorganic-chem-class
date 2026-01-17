import json
import os
import urllib.request
import urllib.parse
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION = "textbooks_chunks"
OLLAMA_URL = "http://localhost:11434"
MODEL = "nomic-embed-text"
LLM_MODEL = "qwen3:32b"
OUTPUT_FILE = "data/symmetry_gallery.json"

client = QdrantClient(url=QDRANT_URL)

MOLECULE_TYPES = [
    # Basic Teaching Examples (for Lectures)
    "H2O", "NH3", "CH4", "SF6", "C6H6", "BF3", "PCl5", "CO2", "HCN", "C2H4",
    
    # Classic Coordination (Oh, D4h)
    "[Co(NH3)6]3+", "[PtCl4]2-", "[Ni(CN)4]2-", "[Fe(H2O)6]2+", 
    
    # Isomers (C2v, D2h)
    "cis-[Pt(NH3)2Cl2]", "trans-[Pt(NH3)2Cl2]", 
    "fac-[Co(NH3)3Cl3]", "mer-[Co(NH3)3Cl3]", 
    
    # Chiral / Helical (D3, C2)
    "[Co(en)3]3+", "[Ru(bipy)3]2+", "cis-[Co(en)2Cl2]+",
    
    # Tetrahedral (Td)
    "[Ni(CO)4]", "[MnO4]-", "[CoCl4]2-",
    
    # Icosahedral (Ih)
    "[B12H12]2-", "C60",
    
    # High Symmetry / Special
    "ferrocene", "[Re2Cl8]2-", "IF7"
]

def get_embedding(text):
    url = f"{OLLAMA_URL}/api/embeddings"
    data = json.dumps({"model": MODEL, "prompt": text}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['embedding']
    except Exception as e:
        print(f"Embedding error: {e}")
        return [0.0] * 768

def generate_symmetry_info(molecule, context):
    prompt = f"""
    You are an expert in molecular symmetry.
    Based on the context and your knowledge, provide the symmetry data for the molecule: {molecule}.
    
    CONTEXT:
    {context}
    
    REQUIREMENTS:
    1. Identify the Point Group (e.g., C2v, D3h, Oh).
    2. List KEY symmetry elements (principal axis, planes, etc.).
    3. Provide coordinates for a simple 3D representation (Central atom at 0,0,0).
    4. Output strictly in JSON format.

    JSON FORMAT:
    {{
        "name": "{molecule}",
        "pointGroup": "C2v",
        "elements": ["C2 axis along z", "sigma_v(xz) plane", "sigma_v(yz) plane"],
        "atoms": [
            {{"element": "O", "x": 0, "y": 0, "z": 0}},
            {{"element": "H", "x": 0.757, "y": 0.586, "z": 0}},
            {{"element": "H", "x": -0.757, "y": 0.586, "z": 0}}
        ]
    }}
    """
    
    url = f"{OLLAMA_URL}/api/generate"
    data = json.dumps({
        "model": LLM_MODEL, 
        "prompt": prompt, 
        "stream": False,
        "format": "json"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return json.loads(result['response'])
    except Exception as e:
        print(f"Generation error: {e}")
        return None

def main():
    print("Generating Symmetry Gallery Data...")
    gallery = []
    
    for mol in MOLECULE_TYPES:
        print(f"Processing {mol}...")
        vector = get_embedding(f"symmetry point group structure of {mol}")
        
        try:
            search_result = client.query_points(
                collection_name=COLLECTION,
                query=vector,
                using="dense",
                limit=3,
                with_payload=True
            ).points
            
            context = "\n\n".join([hit.payload.get('text', '') for hit in search_result])
            
            data = generate_symmetry_info(mol, context)
            if data:
                gallery.append(data)
                print(f"  + Added {mol}")
                
        except Exception as e:
            print(f"  Error: {e}")
            
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(gallery, f, indent=2)
    print(f"Saved {len(gallery)} molecules to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
