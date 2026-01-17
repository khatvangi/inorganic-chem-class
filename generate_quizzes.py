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
LLM_MODEL = "qwen3:32b"      # Higher quality reasoning
CONFIG_FILE = "data/quiz_config.json"
OUTPUT_DIR = "data/quizzes"

os.makedirs(OUTPUT_DIR, exist_ok=True)

client = QdrantClient(url=QDRANT_URL)

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

def generate_question(context, topic):
    prompt = f"""
    You are an expert inorganic chemistry professor.
    Based ONLY on the following context, create a high-quality multiple-choice question about "{topic}".
    
    CRITICAL: You must provide data to render a 3D molecule of the subject of the question using ChemDoodle.
    
    CONTEXT:
    {context}
    
    REQUIREMENTS:
    1. Question must be challenging and conceptually sound.
    2. Provide 4 options (A, B, C, D).
    3. Indicate the correct answer.
    4. Provide a brief explanation/rationale.
    5. **Extract structural data**: formula, central atom, geometry, and ligand arrangement (top, bottom, left, right, front, back).
    6. Output strictly in JSON format.

    JSON FORMAT:
    {{
        "question": "Question text...",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "explanation": "Rationale...",
        "formula": "[M(L)n]X",
        "geometry": "Octahedral", 
        "diagram": {{
            "central": "M",
            "ligands": {{
                "top": "L",
                "bottom": "L",
                "left": "L",
                "right": "L",
                "front": "L", 
                "back": "L"
            }}
        }}
    }}
    (Note: For 'geometry', use standard terms: Octahedral, Tetrahedral, Square Planar, Linear, Trigonal Bipyramidal. Omit unused positions in 'ligands'.)
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
    print("Loading configuration...")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    for module in config['modules']:
        print(f"\nProcessing Module: {module['title']}")
        questions = []
        
        for topic in module['topics']:
            print(f"  > Topic: {topic}")
            
            vector = get_embedding(topic)
            try:
                search_result = client.query_points(
                    collection_name=COLLECTION,
                    query=vector,
                    using="dense",
                    limit=3,
                    with_payload=True
                ).points
                
                context = "\n\n".join([hit.payload.get('text', '') for hit in search_result])
                
                for _ in range(3):
                    q_data = generate_question(context, topic)
                    if q_data:
                        q_data['topic'] = topic
                        q_data['module'] = module['id']
                        # Sanitize geometry for ChemDoodle mapping
                        if 'geometry' in q_data:
                            q_data['geometry'] = q_data['geometry'].lower()
                        questions.append(q_data)
                        print("    + Generated question with structure")
                        
            except Exception as e:
                print(f"    Error: {e}")
        
        outfile = os.path.join(OUTPUT_DIR, f"{module['id']}.json")
        with open(outfile, 'w') as f:
            json.dump(questions, f, indent=2)
        print(f"Saved {len(questions)} questions to {outfile}")

if __name__ == "__main__":
    main()
